import json
import keyboard as kb
import pyautogui
import subprocess
import webbrowser
import time
import yaml
from julep import Julep
from window_utils import get_active_window
from window_utils import get_all_open_windows
import dotenv
import os
import pyttsx3 
import pyperclip
import threading
from dotenv import load_dotenv

load_dotenv()

class CommandHandler:
    PROMPT_TEMPLATE = """
        Analyze requests through this decision framework:

        1. Request Type Detection:
        - Action Requests: Require system interactions (use commands)
        - Information Requests: Need knowledge responses (use llm_response)
        - Hybrid Requests: Combine both action and information

        2. Execution Considerations:
        a. Application Startup: 
        - Use 'start app_name' for Windows programs (e.g., 'start excel')
        - For Store apps: 'start shell:appsFolder\PackageName!App'
        - Complex paths: 'start "" "C:/Path/To App.exe"'
        - System handles window waiting automatically (no long sleeps needed)
        b. Window Context: Use shortcuts specific to {window_title}
        c. Multi-step Sequencing: Break complex tasks into ordered steps
        - Group related commands without sleeps between them
        d. Error Prevention: 
        - Add focus commands (click/move) before text input
        - For unregistered apps: Use Win+R fallback strategy

        3. Command Selection Guide:
        - System Control: 
        run_command (Windows: 'start appname' or full quoted paths),
        press_keys, open_url
        - Application Launch Priority:
        1. Try press_keys shortcuts first (Alt+Tab, Win+Number)
        2. Use 'run_command' with 'start' for known apps
        3. Registry lookup for installed apps
        4. Full quoted paths for complex installations
        - Mouse Actions: left_click, right_click, scroll, move_mouse, hold_mouse, release_mouse
        - Information: llm_response (verbal) OR type_text (direct input)
        - Flow Control: Minimal 0.1-0.3s sleeps between input actions
        - Speech Control: speak_text, stop_speaking, read_from_cursor
            
        4. Key Press Optimization:
        - Press multiple keys simultaneously via press_keys
        - Example: ['ctrl','shift','esc'] for Task Manager
        - Always try key combinations before complex solutions
        
        5.abrogate is for stop listening
        
        Available Commands: {commands}
        Current Window: {window_title}

        Examples:
        1. "Quick app launch sequence"
        [
            {{"command": "run_command", "parameters": {{"command": "notepad"}}}},
            {{"command": "run_command", "parameters": {{"command": "calc"}}}},
            {{"command": "press_keys", "parameters": {{"keys": ["alt","tab"]}}}}
        ]

        2. "Efficient browser research"
        [
            {{"command": "open_url", "parameters": {{"url": "https://www.google.com"}}}},
            {{"command": "type_text", "parameters": {{"text": "AI trends"}}}},
            {{"command": "press_keys", "parameters": {{"keys": ["enter"]}}}},
            {{"command": "sleep", "parameters": {{"duration": 0.3}}}},
            {{"command": "llm_response", "parameters": {{"text": "Here are the latest trends..."}}}}
        ]

        3. "Photo editing workflow"
        [
            {{"command": "run_command", "parameters": {{"command": "start photoshop"}}}},
            {{"command": "move_mouse", "parameters": {{"move_x": 0.3, "move_y": 0.8}}}},
            {{"command": "left_click"}},
            {{"command": "press_keys", "parameters": {{"keys": ["ctrl","o"]}}}}
        ]

        4. "Admin command example"
        [
            {{"command": "run_command", 
            "parameters": {{"command": "runas /user:Administrator cmd.exe"}}}}
        ]
        
        5. "Speaking response example"
        [
            {{"command": "llm_response", "parameters": {{"text": "Here's the weather forecast."}}}},
            {{"command": "speak_text", "parameters": {{"text": "The weather today is sunny with a high of 75 degrees."}}}}
        ]

        6. "Read selected text"
        [
            {{"command": "read_from_cursor"}},
            {{"command": "sleep", "parameters": {{"duration": 0.5}}}}
        ]

        7. "Stop speech example"
        [
            {{"command": "stop_speaking"}}
        ]

        Critical Rules:
        - NEVER use long sleeps after run_command/open_url - system auto-waits
        - Use 0.1-0.3s sleeps only between typing/click actions
        - Wrap spaces in paths: "C:/Program Files/"
        - Use 'start ""' for quoted paths
        - Fallback sequence: Win+R → Type name → Enter
        - Prefer key combos over mouse movements
        - Verify admin rights when needed

        Request: {text}
        Respond ONLY with a valid JSON array:
    """

    def __init__(self, assistant=None, julep_api_key=None):
        self.assistant = assistant
        self.actions = {
            'press_keys': self.press_keys,
            'run_command': self.run_system_command,
            'type_text': self.type_text,
            'open_url': webbrowser.open,
            'abrogate': self.pause_command,
            'left_click': self.left_click,
            'right_click': self.right_click,
            'scroll': self.scroll,
            'move_mouse': self.move_mouse,
            'llm_response': self.llm_response,
            'sleep': self.sleep,
            'speak_text': self.speak_text,
            'read_from_cursor': self.read_from_cursor,
            'stop_speaking': self.stop_speaking,
            'hold_mouse': self.hold_mouse,
            'release_mouse': self.release_mouse,
        }
        
        # Text-to-speech engine setup
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
        except Exception as e:
            if self.assistant:
                self.assistant.log(f"TTS Error: {str(e)}")
            self.engine = None
            
        self.is_speaking = False
        self.speech_thread = None
        
        # Initialize Julep client
        self.client = Julep(api_key=os.environ['JULEP_API_KEY'])
        # Create or reuse the agent
        self.agent = self.client.agents.create(
            name="VoiceControl",
            model="gpt-4o",
            about="System control assistant that outputs valid JSON commands"
        )
        
        # Create the task template
        self.task = self.client.tasks.create(
            agent_id=self.agent.id,
            name="Voice Command Handler",
            description="Interpret user voice command and return system-level actions in JSON",
            main=yaml.safe_load("""
                - prompt:
                  - role: system
                    content: You are a system control agent. Return a JSON array of commands only.
                  - role: user
                    content: $ f\"\"\"{steps[0].input.prompt}\"\"\"
            """)
        )
        
        # Add conversation history
        self.conversation_history = []
        
        # Initialize Julep client
        self.client = Julep(api_key=os.getenv("JULEP_API_KEY"))
        
        # Create or reuse the agent
        self.agent = self.client.agents.create(
            name="VoiceControl",
            model="gpt-4o",
            about="System control assistant that outputs valid JSON commands"
        )
        
        # Create the task template
        self.task = self.client.tasks.create(
            agent_id=self.agent.id,
            name="Voice Command Handler",
            description="Interpret user voice command and return system-level actions in JSON",
            main=yaml.safe_load("""
                - prompt:
                  - role: system
                    content: You are a system control agent. Return a JSON array of commands only.
                  - role: user
                    content: $ f\"\"\"{steps[0].input.prompt}\"\"\"
            """)
        )

    def speak_text(self, text="", **kwargs):
        """Handle text-to-speech output in background thread"""
        if not text or not self.engine:
            return
            
        if self.is_speaking:
            self.stop_speaking()

        def run_speech():
            self.is_speaking = True
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                if self.assistant:
                    self.assistant.log(f"Speech Error: {str(e)}")
            finally:
                self.is_speaking = False

        self.speech_thread = threading.Thread(target=run_speech)
        self.speech_thread.start()
        
    def hold_mouse(self, **kwargs):
        """Press and hold mouse button at current position"""
        button = kwargs.get('button', 'left')
        pyautogui.mouseDown(button=button)

    def release_mouse(self, **kwargs):
        """Release previously held mouse button"""
        button = kwargs.get('button', 'left')
        pyautogui.mouseUp(button=button)

    def read_from_cursor(self, **kwargs):
        """Read text from current cursor position by simulating selection"""
        try:
            original_clipboard = pyperclip.paste()
            selected_text = ""
            
            # Clear existing selection and position cursor
            pyautogui.press('esc')
            time.sleep(0.2)
            
            # Select from cursor position using keyboard
            pyautogui.hotkey('shift', 'end')  # Select to line end
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)
            current_text = pyperclip.paste().strip()
            
            if current_text:
                # Expand selection downward
                for _ in range(10):  # Max 10 paragraphs
                    pyautogui.hotkey('shift', 'down')
                    time.sleep(0.2)
                    pyautogui.hotkey('ctrl', 'c')
                    time.sleep(0.3)
                    new_text = pyperclip.paste().strip()
                    if not new_text or new_text == current_text:
                        break
                    current_text = new_text
                    
                selected_text = current_text.replace('\n', ' ')  # Clean newlines

            # Restore original clipboard
            pyperclip.copy(original_clipboard)
            
            if selected_text:
                self.speak_text(text=selected_text)
            elif self.assistant:
                self.assistant.log("No text detected")
                
        except Exception as e:
            if self.assistant:
                self.assistant.log(f"Read Error: {str(e)}")

    def stop_speaking(self, **kwargs):
        """Force-stop speech with engine reset"""
        if self.engine:
            # Stop current speech
            self.engine.stop()
            # Reset engine state
            if self.engine._driver:
                self.engine._driver.stop()
            if self.engine._inLoop:
                self.engine.endLoop()
            # Reinitialize engine
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 150)
                self.engine.setProperty('volume', 0.9)
            except Exception as e:
                if self.assistant:
                    self.assistant.log(f"TTS Reset Error: {str(e)}")
        
        self.is_speaking = False
        # Clean up speech thread
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=0.2)
        
    def sleep(self, duration=1, **kwargs):
        """Add delay between commands"""
        time.sleep(float(duration))
        
    def llm_response(self, text="", **kwargs):
        """Handle verbal response through GUI"""
        if self.assistant and self.assistant.gui and text:
            self.assistant.gui.log(f"Assistant: {text}")

    def generate_commands(self, text):
        try:
            current_window = get_active_window()
            
            # Build context-aware prompt
            context = "\n".join(
                f"User: {msg['user']}\nAssistant: {msg['assistant']}" 
                for msg in self.conversation_history[-3:]  # Keep last 3 exchanges
            )
            
            # Format the main template first
            main_prompt = self.PROMPT_TEMPLATE.format(
                window_title=current_window,
                commands=list(self.actions.keys()),
                text=text
            )
            
            # Combine with context
            prompt = f"Previous conversation context:\n{context}\n\n{main_prompt}"
            
            execution = self.client.executions.create(
                task_id=self.task.id,
                input={"prompt": prompt}
            )

            while True:
                result = self.client.executions.get(execution.id)
                if result.status in ['succeeded', 'failed']:
                    break
                time.sleep(0.5)
            
            if result.status == "succeeded":
                if isinstance(result.output, dict):
                    raw_text = result.output.get('choices', [{}])[0].get('message', {}).get('content', '')
                else:
                    raw_text = str(result.output)
                
                clean_text = raw_text.replace('```json', '').replace('```', '').strip()
                
                try:
                    commands = json.loads(clean_text)
                    # Update conversation history
                    self.conversation_history.append({
                        'user': text,
                        'assistant': raw_text,
                        'window': current_window,
                        'timestamp': time.time()
                    })
                    return commands
                except json.JSONDecodeError:
                    start_idx = clean_text.find('[')
                    end_idx = clean_text.rfind(']') + 1
                    if start_idx != -1 and end_idx != 0:
                        commands = json.loads(clean_text[start_idx:end_idx])
                        self.conversation_history.append({
                            'user': text,
                            'assistant': clean_text[start_idx:end_idx],
                            'window': current_window,
                            'timestamp': time.time()
                        })
                        return commands
                    raise
            else:
                if self.assistant:
                    self.assistant.log(f"Julep AI failed: {result.error}")
                return []
                
        except Exception as e:
            if self.assistant:
                self.assistant.log(f"Command processing failed: {e}")
            return []

    # Command implementations (remain the same as before)
    def left_click(self, **kwargs):
        pyautogui.click()
        
    def right_click(self, **kwargs):
        pyautogui.rightClick()
        
    def scroll(self, scroll_amount=5, **kwargs):
        pyautogui.scroll(int(scroll_amount))
        
    def move_mouse(self, move_x=0.5, move_y=0.5, **kwargs):
        screen_width, screen_height = pyautogui.size()
        x = int(float(move_x) * screen_width)
        y = int(float(move_y) * screen_height)
        pyautogui.moveTo(x, y, duration=0.5)

    def press_keys(self, keys=[], **kwargs):
        try:
            if len(keys) > 1:
                kb.send("+".join(keys))
            elif keys:
                kb.press_and_release(keys[0])
        except Exception as e:
            print(f"Key press failed: {e}")

    def run_system_command(self, command="", **kwargs):
        try:
            command = f'cmd /c "{command}"' if not command.startswith('cmd ') else command
            
            subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True
        except Exception as e:
            self.assistant.log(f"Command execution error: {str(e)}")
            return False

    def type_text(self, text: str = "", delay: float = 0.05):
            """
            Prints the text to stdout and “types” it via the keyboard library,
            pausing delay seconds between each keystroke.
            """
            if not text:
                return

            print(text)  # still print it out
            for char in text:
                kb.write(char)
                time.sleep(delay)

    def pause_command(self, **kwargs):
        if self.assistant:
            self.assistant.activated = False
            self.assistant.log("🛑 Deactivated. Say 'arise' to wake me.")
            if self.assistant.gui:
                self.assistant.gui.update_status("waiting")