from openai import OpenAI
from dotenv import load_dotenv
load_dotenv(override=True)
import os
import json
import time

def msg(content: str, role: str):
    return {
        "role": role,
        "content": content,
    }

class AI:
    def __init__(self):
        self.reasoning_effort = os.getenv('REASONING_EFFORT', '')
        self.reasoning_effort = str(self.reasoning_effort).lower() if str(self.reasoning_effort).lower() in ['high', 'medium', 'low'] else None
        self.use_response_format = os.getenv('USE_RESPONSE_FORMAT', False)
        self.use_response_format = True if str(self.use_response_format).lower() in ['true', 'yes', 'si'] else False

        base_url = os.getenv('BASE_URL', False)
        api_key = os.getenv('API_KEY', 'open-source')

        if base_url:
            self.client = OpenAI(
                base_url=base_url,
                api_key=api_key,    
            )
        else:
            self.client = OpenAI(
                api_key=api_key
            )

        self.model = os.getenv('AI_MODEL', '')

    @staticmethod
    def getSchema(canBeNull: bool, fieldName: str, type: str, enum):
        schema_name = ''.join(c if c.isalnum() else '_' for c in fieldName).strip('_').lower()
        if not schema_name:
            schema_name = 'response_schema'

        if type == "string":
            content_schema = {
                "type": "string",
                "description": f"Valor para el campo {fieldName}"
            }

        elif type == "date":
            content_schema = {
                "type": "object",
                "properties": {
                    "day": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 31
                    },
                    "month": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 12
                    },
                    "year": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 2100
                    }
                },
                "required": ["day", "month", "year"],
                "additionalProperties": False
            }

        elif type == "enum":
            if not enum:
                raise ValueError("enum type requires enum list")

            content_schema = {
                "type": "string",
                "enum": enum,
                "description": f"Selecciona uno de los valores permitidos para {fieldName}"
            }

        else:
            raise ValueError("type must be string, date or enum")

        if not canBeNull:
            schema = {
                "type": "object",
                "properties": {
                    "leaveEmpty": {
                        "type": "boolean",
                        "const": False
                    },
                    "content": content_schema
                },
                "required": ["leaveEmpty", "content"],
                "additionalProperties": False
            }
        else:
            nullable_content_schema = {
                "anyOf": [
                    content_schema,
                    {"type": "null"}
                ]
            }

            schema = {
                "type": "object",
                "properties": {
                    "leaveEmpty": {
                        "type": "boolean",
                        "description": "True para dejar vacío; false para completar content"
                    },
                    "content": nullable_content_schema
                },
                "required": ["leaveEmpty", "content"],
                "additionalProperties": False
            }

        return {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": schema
            }
        }

    def getResponse(self, messages: list, parser = False):
        max_retries = 7
        wait_time = 1

        for attempt in range(max_retries + 1):
            try:
                if parser:
                    completion = self.client.chat.completions.create(
                        messages=messages,
                        model=self.model,
                        response_format=parser,
                        reasoning_effort=self.reasoning_effort,
                    ).choices[0]
                    return completion.message
                else:
                    completion = self.client.chat.completions.create(
                        messages=messages,
                        model=self.model,
                        reasoning_effort=self.reasoning_effort,
                    ).choices[0]
                    return completion.message
            except:
                if attempt < max_retries:
                    time.sleep(wait_time)
                    wait_time *= 2
                else:
                    return False

    @staticmethod
    def getTextFromShowFields(line: dict, showFields: list[str]):
        fieldTexts = []

        for field in showFields:
            value = line.get(field, '-')
            fieldTexts.append(f'{field}:\n{value}')

        return '\n\n'.join(fieldTexts)

    def fillColumn(self, line: dict, format: dict, column_name: str):
        messages = [
            msg(
                format['prompt'], 
                'system',
            ),
            msg(
                self.getTextFromShowFields(line, format['show_fields']),
                'user',
            ),
        ]

        parser = self.getSchema(
            format.get('can_leave_empty', True), 
            column_name, 
            format.get('type', 'string'), 
            format.get('enum', False)
        ) if self.use_response_format else False

        message = self.getResponse(messages, parser)
        if not message:
            return ''
        
        if not self.use_response_format:
            return message.content

        messageContent = json.loads(message.content)

        if messageContent.get('leaveEmpty', False):
            return ''
        
        return messageContent.get('content', '')
    
    def generateColumns(self, line: dict, formats: dict):
        extra_columns = {}

        for column_name in formats.keys():
            extra_columns[column_name] = self.fillColumn(line, formats[column_name], column_name)

        return extra_columns
    