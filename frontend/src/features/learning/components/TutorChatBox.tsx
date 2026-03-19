"use client";

import React, { useState, useEffect, useRef } from "react";
import { Send, Bot, User, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTranslation } from "@/hooks/use-translation";
import { useLearnStore } from "@/store/useLearnStore";
import { apiClient } from "@/lib/api-client";

export function TutorChatBox({ conceptId }: { conceptId: number }) {
  const { t } = useTranslation();
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { chatHistory, isTutorTyping, addMessage, setTyping } = useLearnStore();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, isTutorTyping]);

  useEffect(() => {
    if (chatHistory.length === 0) {
      addMessage({ role: "tutor", content: t.learning.tutorGreeting });
    }
  }, [chatHistory.length, addMessage, t.learning.tutorGreeting]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMsg = inputValue;
    addMessage({ role: "user", content: userMsg });
    setTyping(true);

    try {
      // Sending history alongside the message ---
      const formattedHistory = chatHistory.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const res = await apiClient<{ response: string }>(
        `/quiz/${conceptId}/chat`,
        {
          method: "POST",
          body: JSON.stringify({
            message: userMsg,
            history: formattedHistory,
          }),
        },
      );
      addMessage({ role: "tutor", content: res.response });
      setInputValue(""); // Clear ONLY on success
    } catch (error) {
      console.error("[TutorChatBox] API Error:", error);
      addMessage({
        role: "tutor",
        content:
          "Sorry, I encountered an error connecting to my brain. Please try again.",
      });
    } finally {
      setTyping(false);
    }
  };

  return (
    <Card className="flex flex-col h-150 border-border shadow-sm">
      <CardHeader className="border-b border-border bg-secondary/30 pb-4 pt-5">
        <CardTitle className="flex items-center gap-2 text-lg">
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary">
            <Sparkles className="w-4 h-4" />
          </div>
          {t.learning.aiTutor}
        </CardTitle>
      </CardHeader>

      {/* Chat Messages Area */}
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatHistory.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.role === "tutor" && (
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 text-primary" />
              </div>
            )}

            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground rounded-tr-sm"
                  : "bg-secondary text-secondary-foreground rounded-tl-sm"
              }`}
            >
              {msg.content}
            </div>

            {msg.role === "user" && (
              <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center shrink-0">
                <User className="w-4 h-4 text-muted-foreground" />
              </div>
            )}
          </div>
        ))}

        {/* Typing Indicator */}
        {isTutorTyping && (
          <div className="flex gap-3 justify-start animate-pulse">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 text-primary" />
            </div>
            <div className="bg-secondary rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce" />
              <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce delay-75" />
              <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce delay-150" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </CardContent>

      {/* Input Area */}
      <div className="p-4 border-t border-border bg-background rounded-b-xl">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={t.learning.chatPlaceholder}
            disabled={isTutorTyping}
            className="flex-1 bg-secondary border border-transparent focus:border-primary/50 focus:ring-1 focus:ring-primary/50 rounded-lg px-4 py-2 text-sm outline-none transition-all disabled:opacity-50"
          />
          <Button
            type="submit"
            size="icon"
            disabled={!inputValue.trim() || isTutorTyping}
            className="shrink-0 rounded-lg"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </Card>
  );
}
