import asyncio
import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch
import httpx

FILE = Path(__file__).resolve().parents[1] / 'smartoken_mcp.py'
spec = importlib.util.spec_from_file_location('smartoken_mcp', FILE)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class ServerTests(unittest.IsolatedAsyncioTestCase):
    async def test_models_and_single_completion(self):
        seen = []
        async def handler(request):
            seen.append(request)
            if request.url.path.endswith('/models'):
                return httpx.Response(200,json={'data':[{'id':'example','pricing':{'input_usd_per_1m_tokens':0.3}}]})
            return httpx.Response(200,json={'choices':[{'message':{'content':'answer'},'finish_reason':'stop'}],'usage':{'total_tokens':7}})
        transport=httpx.MockTransport(handler)
        factory=lambda: httpx.AsyncClient(transport=transport,timeout=20)
        with patch.object(app,'http_client',factory), patch.dict(os.environ,{'SMTOKEN_API_KEY':'test-key'}):
            models=await app.list_models()
            response=await app.chat_completion('example','hello',50)
        self.assertEqual(models['models'][0]['id'],'example')
        self.assertEqual(response['content'],'answer')
        self.assertEqual(response['usage']['total_tokens'],7)
        self.assertEqual(len(seen),2)
        self.assertEqual(seen[1].headers['authorization'],'Bearer test-key')
        self.assertIn(b'"max_tokens":50',seen[1].content)
    async def test_missing_key_and_bad_request_do_not_send(self):
        with patch.dict(os.environ,{},clear=True),patch.object(app,'http_client',side_effect=AssertionError('must not call')):
            with self.assertRaises(ValueError): await app.chat_completion('example','hello',50)
            with self.assertRaises(ValueError): await app.chat_completion('example','',50)
    async def test_onboarding_errors_direct_users_to_the_right_place(self):
        cases = [
            (401, {'error': {'type': 'invalid_request_error'}}, '/dashboard/api-keys', 'API key'),
            (402, {'error': {'type': 'insufficient_quota', 'topup_url': 'https://evil.example/phish'}}, '/dashboard/billing', 'balance'),
            (402, {'error': {'type': 'budget_limit_exceeded'}}, '/dashboard/api-keys', 'budget'),
            (402, {'error': {'type': 'other'}}, '/dashboard/billing', 'check'),
        ]
        for status, body, link, hint in cases:
            with self.subTest(status=status, body=body):
                async def handler(request): return httpx.Response(status, json=body)
                factory = lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=20)
                with patch.object(app, 'http_client', factory), patch.dict(os.environ, {'SMTOKEN_API_KEY': 'test-key'}):
                    with self.assertRaises(RuntimeError) as e: await app.chat_completion('example', 'hello', 50)
                self.assertIn(link, str(e.exception))
                self.assertIn(hint.lower(), str(e.exception).lower())
                self.assertNotIn('evil.example', str(e.exception))

    async def test_missing_key_error_contains_signup_and_key_links(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as e: await app.chat_completion('example', 'hello', 50)
        self.assertIn('https://thesmartoken.com/register', str(e.exception))
        self.assertIn('https://thesmartoken.com/dashboard/api-keys', str(e.exception))

    async def test_server_error_never_retries_or_leaks_body(self):
        count=0
        async def handler(request):
            nonlocal count
            count+=1
            return httpx.Response(502,text='private upstream details')
        factory=lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler),timeout=20)
        with patch.object(app,'http_client',factory),patch.dict(os.environ,{'SMTOKEN_API_KEY':'test-key'}):
            with self.assertRaises(RuntimeError) as e: await app.chat_completion('example','hello',50)
        self.assertEqual(count,1)
        self.assertNotIn('private upstream details',str(e.exception))
        self.assertIn('unknown',str(e.exception).lower())
