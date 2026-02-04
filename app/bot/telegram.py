#!/usr/bin/env python3
"""
AITI Assistant - Telegram Bot
Provides customer service via Telegram using RAG.
"""

import os
import sys
import asyncio
from pathlib import Path
import structlog

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from app.config import settings
from app.rag.vectorstore import VectorStore
from app.rag.chain import RAGChain

logger = structlog.get_logger()

# Initialize components
vectorstore = VectorStore()
rag_chain = RAGChain(vectorstore)

# User conversation state
user_states = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    
    welcome_message = f"""👋 Olá {user.first_name}!

Sou o assistente virtual da **{settings.company_name}**.

Estou aqui para ajudar com as suas questões. Pode perguntar-me sobre:
• 📦 Entregas e prazos
• 💳 Métodos de pagamento
• 🔄 Devoluções e trocas
• 📋 Produtos e serviços

Basta escrever a sua pergunta! 💬"""
    
    keyboard = [
        [InlineKeyboardButton("📖 Perguntas Frequentes", callback_data="faq")],
        [InlineKeyboardButton("👤 Falar com Humano", callback_data="human")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = """🤖 **Como posso ajudar**

Escreva a sua pergunta naturalmente, por exemplo:
• "Qual o prazo de entrega para Lisboa?"
• "Como faço uma devolução?"
• "Têm o produto X disponível?"

**Comandos disponíveis:**
/start - Iniciar conversa
/help - Ver esta ajuda
/novo - Iniciar nova conversa
/humano - Falar com atendente

Se eu não conseguir responder, posso encaminhar para um colega humano! 👨‍💼"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def new_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /novo command - start new conversation."""
    user_id = update.effective_user.id
    if user_id in user_states:
        del user_states[user_id]
    
    await update.message.reply_text(
        "🔄 Nova conversa iniciada!\n\nComo posso ajudar?"
    )


async def request_human(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /humano command - escalate to human."""
    user = update.effective_user
    
    message = """👤 **Encaminhamento para Atendente**

Compreendo que prefere falar com um colega humano.

Por favor, deixe:
• 📧 O seu email
• 📝 Um breve resumo da questão

Um dos nossos colaboradores entrará em contacto em breve (horário comercial: 9h-18h).

Obrigado pela compreensão! 🙏"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    
    # Log escalation
    logger.info(
        "Human escalation requested",
        user_id=user.id,
        username=user.username
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages."""
    user = update.effective_user
    user_id = user.id
    message_text = update.message.text
    
    logger.info(
        "Message received",
        user_id=user_id,
        username=user.username,
        message=message_text[:50]
    )
    
    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    # Get conversation history
    history = user_states.get(user_id, [])
    
    try:
        # Process through RAG
        result = rag_chain.query(
            query=message_text,
            mode="standard",
            conversation_history=history
        )
        
        response_text = result["response"]
        confidence = result["confidence"]
        escalate = result["escalate"]
        
        # Update conversation history
        history.append({"role": "user", "content": message_text})
        history.append({"role": "assistant", "content": response_text})
        user_states[user_id] = history[-10:]  # Keep last 10 messages
        
        # Prepare response with optional escalation button
        if escalate or confidence < 0.5:
            keyboard = [[InlineKeyboardButton("👤 Falar com Humano", callback_data="human")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if confidence < 0.5:
                response_text += "\n\n_Se esta resposta não for suficiente, posso encaminhar para um colega._"
            
            await update.message.reply_text(
                response_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(response_text)
        
        logger.info(
            "Response sent",
            user_id=user_id,
            confidence=confidence,
            escalate=escalate
        )
        
    except Exception as e:
        logger.error("Failed to process message", error=str(e))
        await update.message.reply_text(
            "Peço desculpa, ocorreu um erro. Por favor, tente novamente ou use /humano para falar com um atendente."
        )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "faq":
        faq_text = """📖 **Perguntas Frequentes**

**1. Qual o prazo de entrega?**
Lisboa e Porto: 24-48h úteis
Resto do país: 2-3 dias úteis

**2. Quais os métodos de pagamento?**
MB Way, Cartão, Transferência, Paypal

**3. Como faço uma devolução?**
Tem 14 dias para devolver. Contacte-nos para obter etiqueta de devolução.

**4. Como acompanho a minha encomenda?**
Receberá email com tracking quando expedida.

---
Tem outra questão? Escreva-me! 💬"""
        
        await query.edit_message_text(faq_text, parse_mode="Markdown")
    
    elif query.data == "human":
        await query.edit_message_text(
            "👤 **Encaminhamento Solicitado**\n\n"
            "Por favor, deixe o seu email e um breve resumo.\n"
            "Entraremos em contacto em breve!",
            parse_mode="Markdown"
        )


def main():
    """Start the Telegram bot."""
    if not settings.telegram_bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not configured")
        print("   Set it in .env file")
        sys.exit(1)
    
    print("=" * 50)
    print("🤖 AITI Assistant - Telegram Bot")
    print(f"   Company: {settings.company_name}")
    print(f"   LLM: {settings.llm_model}")
    print("=" * 50)
    
    # Create application
    application = Application.builder().token(settings.telegram_bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ajuda", help_command))
    application.add_handler(CommandHandler("novo", new_conversation))
    application.add_handler(CommandHandler("humano", request_human))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    print("✅ Bot started! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
