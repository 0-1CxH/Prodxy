import unittest
from unittest.mock import MagicMock
import json
from prodxy.operation.llm_request import LLMRequest, LLMResponse, LLMResponsePostProcess

class TestLLMResponse(unittest.TestCase):
    def test_llm_response_init(self):
        resp = LLMResponse(success=True, parsed_response="test")
        self.assertTrue(resp.success)
        self.assertEqual(resp.parsed_response, "test")
        self.assertIsNone(resp.error_message)

class TestLLMResponsePostProcess(unittest.TestCase):
    def test_strip_thinking(self):
        self.assertEqual(LLMResponsePostProcess.strip_thinking("hello"), "hello")
        self.assertEqual(LLMResponsePostProcess.strip_thinking("<think>hmm</think>hello"), "hello")
        self.assertEqual(LLMResponsePostProcess.strip_thinking("  <think>hmm</think>  hello  "), "hello")
        self.assertIsNone(LLMResponsePostProcess.strip_thinking(123))
        # Test malformed
        self.assertEqual(LLMResponsePostProcess.strip_thinking("no end tag"), "no end tag")

    def test_extract_bool(self):
        # True cases
        for val in ['True', 'true', 'TRUE', 'yes', '1', '是', '  true  ']:
            self.assertTrue(LLMResponsePostProcess.extract_bool(val), f"Failed for {val}")
        
        # False cases
        for val in ['False', 'false', 'FALSE', 'no', '0', '否', '  false  ']:
            self.assertFalse(LLMResponsePostProcess.extract_bool(val), f"Failed for {val}")
            
        # Embedded cases
        self.assertTrue(LLMResponsePostProcess.extract_bool("The answer is true."))
        self.assertFalse(LLMResponsePostProcess.extract_bool("The answer is false."))
        
        # None cases
        self.assertIsNone(LLMResponsePostProcess.extract_bool("idk"))
        self.assertIsNone(LLMResponsePostProcess.extract_bool(123))

    def test_extract_json(self):
        # Markdown JSON
        json_str = '{"a": 1}'
        self.assertEqual(LLMResponsePostProcess.extract_json(f"```json\n{json_str}\n```"), {"a": 1})
        
        # XML-like
        self.assertEqual(LLMResponsePostProcess.extract_json(f"<json>\n{json_str}\n</json>"), {"a": 1})
        
        # Plain code block
        self.assertEqual(LLMResponsePostProcess.extract_json(f"```\n{json_str}\n```"), {"a": 1})
        
        # Plain string
        self.assertEqual(LLMResponsePostProcess.extract_json(json_str), {"a": 1})
        
        # Regex extraction
        text = f"some text before {json_str} some text after"
        self.assertEqual(LLMResponsePostProcess.extract_json(text), {"a": 1})
        
        # Fallback
        text = "just text"
        self.assertEqual(LLMResponsePostProcess.extract_json(text), {"response": "just text"})
        
        # Non-dict result (e.g. list)
        self.assertEqual(LLMResponsePostProcess.extract_json("[1, 2]"), {"result": [1, 2]})


class TestLLMRequest(unittest.TestCase):
    def test_call_success(self):
        mock_func = MagicMock(return_value="response")
        resp = LLMRequest.call(mock_func, prompt="hi")
        self.assertTrue(resp.success)
        self.assertEqual(resp.raw_response, "response")
        self.assertEqual(resp.parsed_response, "response")
        mock_func.assert_called_once()

    def test_call_retry_success(self):
        # Fail twice then succeed
        mock_func = MagicMock(side_effect=[Exception("fail"), Exception("fail"), "success"])
        resp = LLMRequest.call(mock_func, prompt="hi", retey_times=3)
        self.assertTrue(resp.success)
        self.assertEqual(resp.parsed_response, "success")
        self.assertEqual(mock_func.call_count, 3)

    def test_call_retry_fail(self):
        # Fail always
        mock_func = MagicMock(side_effect=Exception("fail"))
        resp = LLMRequest.call(mock_func, prompt="hi", retey_times=2)
        self.assertFalse(resp.success)
        self.assertIsNotNone(resp.error_message)
        self.assertEqual(mock_func.call_count, 3) # 0, 1, 2 attempts

    def test_call_bool_target(self):
        mock_func = MagicMock(return_value="true")
        resp = LLMRequest.call(mock_func, target="bool", prompt="is it?")
        self.assertTrue(resp.success)
        self.assertTrue(resp.parsed_response)
        # Check prompt injection
        args, _ = mock_func.call_args
        # kwargs are in the second element of call_args if positional, but here passed as kwargs
        _, kwargs = mock_func.call_args
        self.assertIn(LLMRequest.BOOL_REQ_PROMPT, kwargs['prompt'])

    def test_call_json_target(self):
        mock_func = MagicMock(return_value='{"a": 1}')
        resp = LLMRequest.call(mock_func, target="json", prompt="give json")
        self.assertTrue(resp.success)
        self.assertEqual(resp.parsed_response, {"a": 1})
        _, kwargs = mock_func.call_args
        self.assertIn(LLMRequest.JSON_REQ_PROMPT, kwargs['prompt'])

if __name__ == '__main__':
    unittest.main()
