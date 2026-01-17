# Telegram Configuration Example

This file shows how to configure Telegram alerts for the Linux Monitoring and Alerting Tool.

## Step 1: Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send the command `/newbot`
3. Follow the instructions to create your bot
4. BotFather will give you a token that looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

## Step 2: Get Your Chat ID

1. Search for [@userinfobot](https://t.me/userinfobot) in Telegram
2. Start a chat with the bot
3. It will show you your chat ID (a number like `123456789`)

Alternatively, you can:
1. Send a message to your bot
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for the `"chat":{"id":` field in the response

## Step 3: Configure the Environment Variables

### Option 1: Export in Shell (Temporary)

```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="123456789"
```

### Option 2: Add to /etc/environment (Persistent)

```bash
sudo bash -c 'echo "TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz" >> /etc/environment'
sudo bash -c 'echo "TELEGRAM_CHAT_ID=123456789" >> /etc/environment'
```

### Option 3: Use Systemd Environment File (Recommended for systemd service)

1. Create the environment file:

```bash
sudo mkdir -p /etc/linux-monitoring-alerts
sudo cat > /etc/linux-monitoring-alerts/telegram.env << 'EOF'
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
EOF
sudo chmod 600 /etc/linux-monitoring-alerts/telegram.env
```

2. Edit `/etc/systemd/system/linux-monitoring.service` and uncomment the line:

```ini
EnvironmentFile=/etc/linux-monitoring-alerts/telegram.env
```

3. Reload systemd:

```bash
sudo systemctl daemon-reload
sudo systemctl restart linux-monitoring.timer
```

## Step 4: Test the Integration

Run the monitoring script manually with environment variables set:

```bash
TELEGRAM_BOT_TOKEN="your_token" TELEGRAM_CHAT_ID="your_chat_id" ./scripts/monitor.sh
```

## Example Alert Message

When an alert is triggered, you'll receive a message in Telegram like:

```
🚨 Linux Monitoring Alert - server01

⚠️ ALERT: Disk usage at 85% (threshold: 80%)
⚠️ ALERT: Service nginx is stopped

Timestamp: Fri Jan 17 05:30:00 UTC 2026
```

## Security Notes

- Keep your bot token secret
- Never commit tokens to version control
- Use appropriate file permissions (600) for environment files
- Consider using a dedicated Telegram group for alerts
- You can create different bots for different servers
