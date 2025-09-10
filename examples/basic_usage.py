#!/usr/bin/env python3
"""
Basic usage example for the Temp Mail Python library.

This example demonstrates how to:
1. Create a temporary email address
2. List available domains
3. Check for received messages
4. Delete messages
"""

import os
import time
from tempmail import TempMailClient, CreateEmailOptions


def main():
    # Initialize the client with your API key
    api_key = os.getenv("TEMPMAIL_API_KEY")
    if not api_key:
        print("Please set the TEMPMAIL_API_KEY environment variable")
        return

    client = TempMailClient(api_key)

    try:
        # 1. List available domains
        print("Getting available domains...")
        domains = client.list_domains()
        print(f"Available domains: {[d.domain for d in domains[:5]]}")  # Show first 5

        # 2. Create a temporary email address
        print("\nCreating a temporary email address...")

        # Option 1: Let the API choose a random email
        email = client.create_email()
        print(f"Created email: {email.email}")

        # Option 2: Create with specific domain and prefix
        if domains:
            options = CreateEmailOptions(
                domain=domains[0].domain,
                prefix="mytest"
            )
            custom_email = client.create_email(options)
            print(f"Created custom email: {custom_email.email}")

        # 3. Check for messages (initially should be empty)
        print(f"\nChecking messages for {email.email}...")
        messages = client.list_email_messages(email.email)
        print(f"Current messages: {len(messages)}")

        # 4. Send a test email to the temporary address
        print(f"\nYou can now send test emails to: {email.email}")
        print("Waiting 10 seconds to check for new messages...")
        time.sleep(10)

        # 5. Check for new messages
        messages = client.list_email_messages(email.email)
        print(f"Messages after waiting: {len(messages)}")

        for i, message in enumerate(messages):
            print(f"\nMessage {i+1}:")
            print(f"  From: {message.from_addr}")
            print(f"  Subject: {message.subject}")
            print(f"  Body: {message.body_text[:100]}...")  # First 100 chars

            # 6. Delete the message
            print(f"  Deleting message {message.id}...")
            client.delete_message(message.id)
            print("  Message deleted!")

        # 7. Check rate limit information
        rate_limit = client.get_rate_limit()
        if rate_limit:
            print(f"\nRate limit info:")
            print(f"  Limit: {rate_limit.limit}")
            print(f"  Remaining: {rate_limit.remaining}")
            print(f"  Reset: {rate_limit.reset}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
