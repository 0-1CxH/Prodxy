from typing import Callable
import time
import re
import requests
import traceback
import json
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class LLMResponse:
    success: bool
    error_message: Optional[str] = None
    prompt: Optional[Dict] = None
    raw_response: Optional[str] = None
    parsed_response: Optional[str] = None


class RawLLMRequest:
    
    @staticmethod
    def by_curl(**kwargs):
        api_url = kwargs['api_url']
        api_key = kwargs['api_key']
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": kwargs['model'],
            "messages": [{"role": "user", "content": kwargs['prompt']}],
            "stream": kwargs.get('stream', False),
            **kwargs.get('extra_params', {})
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
        


class LLMResponsePostProcess:
    @staticmethod
    def strip_thinking(resp):
        if not isinstance(resp, str):
            return None
        if "</think>" in resp:
            try:
                return resp.split("</think>", 1)[1].strip()
            except Exception:
                return resp.strip()
        return resp.strip()
    
    @staticmethod
    def extract_bool(resp):
        if not isinstance(resp, str):
            return None
        response_lower = resp.strip().lower()
        if response_lower in ['true', 'yes', '1', '是']:
            return True
        elif response_lower in ['false', 'no', '0', '否']:
            return False
        else:
            if 'true' in response_lower:
                return True
            if 'false' in response_lower:
                return False
        return None
    
    @staticmethod
    def extract_json(resp):
        json_data = None
        try:
            # Try to extract JSON content from code block
            if "```json" in resp and "```" in resp.split("```json", 1)[1]:
                json_content = resp.split("```json", 1)[1].split("```")[0].strip()
            elif "<json>" in resp and "</json>" in resp.split("</json>", 1)[1]:
                json_content = resp.split("</json>", 1)[1].split("</json>")[0].strip()
            elif "```" in resp:
                # Try to extract from any code block
                json_content = resp.split("```", 2)[1].strip()
            else:
                json_content = resp.strip()
            
            # Safely parse JSON
            json_data = json.loads(json_content)
            
            if not isinstance(json_data, dict):
                json_data = {"result": json_data}
        except json.JSONDecodeError:
            # if can not decode, try extract using regex
            json_pattern = r'\{[^{}]*\}'
            matches = re.findall(json_pattern, resp)
            if matches:
                json_data = json.loads(matches[0])
            else:
                # if everything fails, create a dict of str resp
                json_data = {"response": resp}
        return json_data


class LLMRequest:
    BOOL_REQ_PROMPT = "\nPlaese analyze the given question, and only return 'TRUE' or 'FALSE' as the answer. Do not include any other explanation or content."
    JSON_REQ_PROMPT = "\nPlease analyze the given question, and only return a valid JSON string as the answer. Do not include any other explanation or content."

    @staticmethod
    def call(raw_request_func:Callable = RawLLMRequest.by_curl, target: str = "string", **kwargs):
        retry_times=int(kwargs.get('retey_times', 3))
        for attempt in range(retry_times + 1):
            try:
                if 'bool' == target.lower():
                    kwargs['prompt'] += LLMRequest.BOOL_REQ_PROMPT
                if 'json' == target.lower():
                    kwargs['prompt'] += LLMRequest.JSON_REQ_PROMPT
                resp = raw_request_func(**kwargs)
                parsed_resp = LLMResponsePostProcess.strip_thinking(resp)
                if 'bool' == target.lower():
                    parsed_resp = LLMResponsePostProcess.extract_bool(parsed_resp)
                if 'json' == target.lower():
                    parsed_resp = LLMResponsePostProcess.extract_json(parsed_resp)
                return LLMResponse(
                    success=True,
                    error_message=None,
                    prompt=kwargs['prompt'],
                    raw_response=resp,
                    parsed_response=parsed_resp
                )
                
            except Exception as e:
                if attempt == retry_times:
                    return LLMResponse(
                        success=False,
                        error_message=traceback.format_exc()
                    )
                time.sleep(2 ** attempt)