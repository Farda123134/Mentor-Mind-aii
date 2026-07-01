import os
import threading
import logging
import traceback

log = logging.getLogger('MentorMind')

_client = None


def get_client():
    global _client
    if _client is None:
        try:
            from groq import Groq
            key = os.environ.get('GROQ_KEY', '')
            if not key:
                raise ValueError(
                    'GROQ_KEY not set! '
                    'Run: os.environ["GROQ_KEY"] = "your_key"'
                )
            _client = Groq(api_key=key)
            log.info('Groq client initialized')
        except ImportError:
            raise ImportError('groq not installed. Run: pip install groq')
    return _client


def call_ai(system_prompt, user_message, max_tokens=800, timeout=30):
    result = {'text': None, 'error': None, 'tb': None}

    def _call():
        try:
            client   = get_client()
            response = client.chat.completions.create(
                model       = 'llama-3.1-8b-instant',
                messages    = [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user',   'content': user_message}
                ],
                max_tokens  = max_tokens,
                temperature = 0.7
            )
            result['text'] = response.choices[0].message.content
            chars = len(result['text'])
            log.info('AI response: ' + str(chars) + ' chars')
        except Exception as e:
            result['error'] = str(e)
            result['tb']    = traceback.format_exc()
            log.error('call_ai failed: ' + str(e))
            log.error(result['tb'])

    t = threading.Thread(target=_call)
    t.daemon = True
    t.start()
    t.join(timeout=timeout)

    if t.is_alive():
        msg = 'Groq API timed out after ' + str(timeout) + 's'
        log.error(msg)
        return 'Error: ' + msg

    if result['error']:
        tb  = result['tb'] or ''
        msg = 'AI Error: ' + result['error']
        log.error(msg + '\n' + tb)
        return 'Error: ' + result['error']

    return result['text'] or 'Error: Empty response'


def reset_client():
    global _client
    _client = None
    log.info('Groq client reset')
