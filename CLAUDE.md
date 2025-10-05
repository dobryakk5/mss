# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Telegram bot for the "7;0309 OA=>" (Express Clearly) writing course by Elena Lebedeva. The bot provides course information, handles user support, and includes a skills assessment test.

## Architecture

### Core Components

- **bot.py**: Main bot file containing all message handlers, database functions, and FSM states
- **test_module.py**: Support module containing test-related keyboards, states, and helper functions
- **PostgreSQL Database**: Stores user data and message logs in two tables:
  - `mss_users`: User profiles (user_id, username, names, timestamps)
  - `mss_chat`: Complete message log (user_id, message_text, message_type, timestamp)

### Key Features

1. **Course Information System**: 7 main menu sections with detailed course content
2. **Support System**: Automatic forwarding of user questions to admin (chat_id: 269435099)
3. **Skills Assessment Test**: 5-question FSM-based test with level determination (>28G>:/#25@5==K9/@>428=CBK9)
4. **Database Logging**: All user interactions and test results are stored

### Message Flow

- All messages trigger `add_user_to_db()` to ensure user tracking
- Messages are logged via `log_message_to_db()` with type classification
- Support questions automatically forward to admin via `bot.send_message(ADMIN_CHAT_ID)`
- Test uses FSM states (TestStates.question1-5) for progression

## Development Commands

### Running the Bot
```bash
python bot.py
```

### Database Connection
- Uses environment variable `DATABASE_URL`
- Tables are auto-created on first run via `init_database()`

### Environment Setup
Required `.env` variables:
- `BOT_TOKEN`: Telegram bot token
- `DATABASE_URL`: PostgreSQL connection string

## Code Patterns

### Adding New Menu Items
1. Add KeyboardButton to `get_main_keyboard()`
2. Create handler with pattern: `@dp.message(lambda message: message.text == "Button Text")`
3. Always include: `await add_user_to_db(message.from_user)` and `await log_message_to_db()`

### Database Operations
- Use `get_db_connection()` for all DB operations
- Always wrap in try/except with proper connection cleanup
- Use asyncpg parameterized queries for safety

### FSM State Management
- Import states from test_module: `from test_module import TestStates`
- Use `@dp.message(StateClass.state_name)` for state-specific handlers
- Always clear state after completion: `await state.clear()`

## Critical Configuration

- **Admin Contact**: `@Lebedeva_Elen` (hardcoded in ELENA_CONTACT)
- **Admin Chat ID**: `269435099` (for support message forwarding)
- **Channel Link**: Currently placeholder "AAK;:0" - update CHANNEL_LINK when available
- **Menu Structure**: 4 rows × 2 columns layout, with test button in bottom row

## Message Type Classifications

Support these types when logging to `mss_chat`:
- `command`: Bot commands (/start)
- `menu_button`: Main menu selections
- `support_question`: User support inquiries
- `test_start`: Test initiation
- `test_result`: Completed test with answers and level
- `other_message`: Unrecognized messages