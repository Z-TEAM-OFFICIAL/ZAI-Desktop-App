#!/usr/bin/env python3
"""
Z-AI Desktop Application
A modern AI chat application using OpenRouter API with MCP support
"""

import os
import sys
import json
import threading
import subprocess
from datetime import datetime

import customtkinter as ctk
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "nvidia/nemotron-3-nano-30b-a3b:free"
APP_NAME = "Z-AI"
APP_VERSION = "1.0.0"

# Colors
COLORS = {
    "bg_primary": "#0d0d0d",
    "bg_secondary": "#1a1a1a",
    "bg_tertiary": "#252525",
    "accent": "#00d4aa",
    "accent_hover": "#00f5c4",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "border": "#333333",
    "user_msg": "#00d4aa",
    "ai_msg": "#2a2a2a"
}


class MCPClient:
    """MCP Server Client"""
    
    def __init__(self, config_path="mcp.json"):
        self.config_path = config_path
        self.servers = {}
        self.processes = {}
        self.load_config()
    
    def load_config(self):
        """Load MCP configuration from mcp.json"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.servers = config.get("mcpServers", {})
                    print(f"Loaded {len(self.servers)} MCP server(s)")
        except Exception as e:
            print(f"Error loading MCP config: {e}")
    
    def start_server(self, name, config):
        """Start an MCP server"""
        if name in self.processes:
            return True
        
        try:
            cmd = [config["command"]] + config.get("args", [])
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, **config.get("env", {})}
            )
            self.processes[name] = proc
            print(f"Started MCP server: {name}")
            return True
        except Exception as e:
            print(f"Error starting MCP server {name}: {e}")
            return False
    
    def stop_server(self, name):
        """Stop an MCP server"""
        if name in self.processes:
            self.processes[name].terminate()
            del self.processes[name]
    
    def stop_all(self):
        """Stop all MCP servers"""
        for name in list(self.processes.keys()):
            self.stop_server(name)


class ChatMessage:
    """Represents a chat message"""
    
    def __init__(self, role, content, timestamp=None):
        self.role = role  # 'user' or 'ai'
        self.content = content
        self.timestamp = timestamp or datetime.now()


class ZAIApp(ctk.CTk):
    """Main Z-AI Application"""
    
    def __init__(self):
        super().__init__()
        
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.messages = []
        self.mcp_client = MCPClient()
        
        self.setup_window()
        self.setup_ui()
        
        if not self.api_key:
            self.show_api_key_dialog()
    
    def setup_window(self):
        """Setup main window"""
        self.title(f"{APP_NAME} - Desktop")
        self.geometry("900x700")
        self.minsize(600, 500)
        
        # Dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # Configure window bg
        self.configure(fg_color=COLORS["bg_primary"])
    
    def setup_ui(self):
        """Setup UI components"""
        # Header
        self.header = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=60)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        
        # Logo
        self.logo_label = ctk.CTkLabel(
            self.header,
            text=f"{APP_NAME}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["accent"]
        )
        self.logo_label.pack(side="left", padx=20)
        
        # Model badge
        self.model_badge = ctk.CTkLabel(
            self.header,
            text="Nemotron Nano A3B 30B (Free)",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            fg_color=COLORS["bg_tertiary"],
            corner_radius=15,
            padx=15,
            pady=5
        )
        self.model_badge.pack(side="left", padx=(0, 10))
        
        # MCP button
        self.mcp_btn = ctk.CTkButton(
            self.header,
            text="MCP Servers",
            command=self.show_mcp_dialog,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            width=100
        )
        self.mcp_btn.pack(side="right", padx=20)
        
        # Clear button
        self.clear_btn = ctk.CTkButton(
            self.header,
            text="Clear",
            command=self.clear_chat,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            width=80
        )
        self.clear_btn.pack(side="right", padx=(0, 10))
        
        # Settings button
        self.settings_btn = ctk.CTkButton(
            self.header,
            text="⚙",
            command=self.show_api_key_dialog,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            width=40
        )
        self.settings_btn.pack(side="right", padx=(0, 10))
        
        # Chat display
        self.chat_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_tertiary"],
            scrollbar_button_hover_color=COLORS["border"]
        )
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            self.chat_frame,
            text="Welcome to Z-AI!",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.welcome_label.pack(pady=50)
        
        self.welcome_sublabel = ctk.CTkLabel(
            self.chat_frame,
            text="Start a conversation with Nemotron Nano A3B 30B\n\nGet your free API key from:\nhttps://openrouter.ai/settings/keys",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        )
        self.welcome_sublabel.pack()
        
        # Input area
        self.input_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], height=80)
        self.input_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.input_frame.pack_propagate(False)
        
        self.input_box = ctk.CTkTextbox(
            self.input_frame,
            fg_color=COLORS["bg_tertiary"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=14),
            wrap="word",
            height=50
        )
        self.input_box.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        self.input_box.bind("<Return>", self.on_enter_key)
        
        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="Send",
            command=self.send_message,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg_primary"],
            width=80,
            height=50
        )
        self.send_btn.pack(side="right", padx=(5, 10), pady=10)
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        self.status_label.pack(fill="x", padx=15, pady=(0, 5))
    
    def on_enter_key(self, event):
        """Handle Enter key press"""
        if event.state & 0x1:  # Shift key
            return
        self.send_message()
        return "break"
    
    def show_api_key_dialog(self):
        """Show API key input dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("API Key Settings")
        dialog.geometry("500x250")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="OpenRouter API Key",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog,
            text="Enter your OpenRouter API key (get free key at\nhttps://openrouter.ai/settings/keys)",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack()
        
        api_entry = ctk.CTkEntry(
            dialog,
            width=400,
            placeholder_text="sk-or-v1-..."
        )
        api_entry.pack(pady=20)
        api_entry.insert(0, self.api_key)
        
        def save_and_close():
            self.api_key = api_entry.get().strip()
            if self.api_key:
                # Save to .env
                with open(".env", "w") as f:
                    f.write(f"OPENROUTER_API_KEY={self.api_key}\n")
                load_dotenv(override=True)
            dialog.destroy()
        
        ctk.CTkButton(
            dialog,
            text="Save",
            command=save_and_close,
            fg_color=COLORS["accent"],
            text_color=COLORS["bg_primary"],
            width=200
        ).pack(pady=10)
    
    def show_mcp_dialog(self):
        """Show MCP servers dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("MCP Servers")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="MCP Servers Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Server list
        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        if not self.mcp_client.servers:
            ctk.CTkLabel(
                scroll,
                text="No MCP servers configured.\nEdit mcp.json to add servers.",
                text_color=COLORS["text_secondary"]
            ).pack(pady=20)
        else:
            for name, config in self.mcp_client.servers.items():
                frame = ctk.CTkFrame(scroll, fg_color=COLORS["bg_tertiary"])
                frame.pack(fill="x", pady=5)
                
                ctk.CTkLabel(
                    frame,
                    text=name,
                    font=ctk.CTkFont(weight="bold"),
                    text_color=COLORS["accent"]
                ).pack(anchor="w", padx=10, pady=(10, 5))
                
                ctk.CTkLabel(
                    frame,
                    text=f"Command: {' '.join(config.get('args', []))}",
                    text_color=COLORS["text_secondary"],
                    font=ctk.CTkFont(size=11)
                ).pack(anchor="w", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy,
            fg_color=COLORS["bg_tertiary"],
            text_color=COLORS["text_primary"],
            width=100
        ).pack(pady=20)
    
    def clear_chat(self):
        """Clear chat history"""
        self.messages = []
        
        # Clear UI
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        
        # Show welcome
        self.welcome_label = ctk.CTkLabel(
            self.chat_frame,
            text="Welcome to Z-AI!",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.welcome_label.pack(pady=50)
        
        self.welcome_sublabel = ctk.CTkLabel(
            self.chat_frame,
            text="Start a conversation with Nemotron Nano A3B 30B",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        )
        self.welcome_sublabel.pack()
        
        self.status_label.configure(text="Chat cleared")
    
    def send_message(self):
        """Send message to API"""
        content = self.input_box.get("1.0", "end-1c").strip()
        if not content or not self.api_key:
            return
        
        # Hide welcome
        if self.messages == []:
            for widget in self.chat_frame.winfo_children():
                widget.destroy()
        
        # Add user message
        self.add_message(content, "user")
        self.messages.append(ChatMessage("user", content))
        self.input_box.delete("1.0", "end")
        
        self.status_label.configure(text="Thinking...")
        
        # Run in thread
        thread = threading.Thread(target=self.get_ai_response, args=(content,))
        thread.daemon = True
        thread.start()
    
    def add_message(self, content, role):
        """Add message to chat display"""
        # Message frame
        msg_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        
        if role == "user":
            msg_frame.pack(anchor="e", pady=5, padx=(50, 0))
            
            # Avatar
            avatar = ctk.CTkLabel(
                msg_frame,
                text="U",
                width=32,
                height=32,
                fg_color=COLORS["accent"],
                text_color=COLORS["bg_primary"],
                corner_radius=16,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            avatar.pack(side="right", padx=(10, 0))
            
            # Content
            content_label = ctk.CTkLabel(
                msg_frame,
                text=content,
                fg_color=COLORS["user_msg"],
                text_color=COLORS["bg_primary"],
                corner_radius=18,
                padx=15,
                pady=10,
                wraplength=500,
                justify="left"
            )
            content_label.pack(side="right")
        else:
            msg_frame.pack(anchor="w", pady=5, padx=(0, 50))
            
            # Avatar
            avatar = ctk.CTkLabel(
                msg_frame,
                text="AI",
                width=32,
                height=32,
                fg_color=COLORS["bg_tertiary"],
                text_color=COLORS["accent"],
                corner_radius=16,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            avatar.pack(side="left", padx=(0, 10))
            
            # Content
            content_label = ctk.CTkLabel(
                msg_frame,
                text=content,
                fg_color=COLORS["ai_msg"],
                text_color=COLORS["text_primary"],
                corner_radius=18,
                padx=15,
                pady=10,
                wraplength=500,
                justify="left"
            )
            content_label.pack(side="left")
        
        # Scroll to bottom
        self.chat_frame._parent_canvas.yview_moveto(1)
    
    def get_ai_response(self, user_message):
        """Get AI response from OpenRouter"""
        try:
            # Prepare messages
            api_messages = [{"role": msg.role, "content": msg.content} for msg in self.messages]
            
            # Add current message
            api_messages.append({"role": "user", "content": user_message})
            
            # Make request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Z-TEAM-OFFICIAL/ZAI-Desktop-App",
                "X-Title": "Z-AI Desktop"
            }
            
            data = {
                "model": MODEL,
                "messages": api_messages,
                "max_tokens": 4096,
                "temperature": 0.7
            }
            
            response = requests.post(API_URL, headers=headers, json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result["choices"][0]["message"]["content"]
                
                self.messages.append(ChatMessage("assistant", assistant_message))
                self.after(0, lambda: self.add_message(assistant_message, "ai"))
                self.after(0, lambda: self.status_label.configure(text="Ready"))
            else:
                error = response.json().get("error", {}).get("message", "Unknown error")
                self.after(0, lambda: self.add_message(f"Error: {error}", "ai"))
                self.after(0, lambda: self.status_label.configure(text="Error"))
        
        except Exception as e:
            self.after(0, lambda: self.add_message(f"Error: {str(e)}", "ai"))
            self.after(0, lambda: self.status_label.configure(text="Error"))
    
    def run(self):
        """Run the application"""
        self.mainloop()


def main():
    """Main entry point"""
    print(f"Starting {APP_NAME} v{APP_VERSION}")
    print(f"Using model: {MODEL}")
    
    app = ZAIApp()
    app.run()


if __name__ == "__main__":
    main()
