const API_KEY = 'svKvhh0O4zGyUB6NisB7tfwUwb6uGUM1JALcUwLR';
const EMAIL = 'ojhashivam81@gmail.com';
const DOMAIN = 'shivamop.tech';
const ZONE_ID = '3021220b0309ca795740ef2ad8adf35f';
const BOT_TOKEN = '7206685163:AAF7cxUTxcKSzsryRmBBIB38Ge8WJQQavJk';
const TELEGRAM_API_URL = https://api.telegram.org/bot${BOT_TOKEN}/sendMessage;

const userStates = {}; // Object to track user states for the IP and subdomain input

// Function to handle requests from Telegram
async function handleRequest(request) {
    const { message } = await request.json();

    if (!message || !message.text) {
        return new Response('Invalid message format', { status: 400 });
    }

    const chatId = message.chat.id;
    const text = message.text.trim();

    // Start command
    if (text === '/start') {
        const welcomeMessage = 👋 Hello! Welcome to the Subdomain Creator Bot!\n\n💡 Use /create to start the subdomain creation process.;
        return sendTelegramMessage(chatId, welcomeMessage);
    }

    // Create command button
    if (text === '/create') {
        userStates[chatId] = { step: 'awaiting_ip' }; // Set user state to await IP input
        const ipRequestMessage = 🖥️ Please enter the IP address for the subdomain.;
        return sendTelegramMessage(chatId, ipRequestMessage);
    }

    // Handle state-based responses
    if (userStates[chatId]?.step === 'awaiting_ip') {
        userStates[chatId].ip = text;
        userStates[chatId].step = 'awaiting_subdomain';
        const subdomainRequestMessage = 🌐 Great! Now enter the subdomain name (e.g., 'mysubdomain').;
        return sendTelegramMessage(chatId, subdomainRequestMessage);
    }

    if (userStates[chatId]?.step === 'awaiting_subdomain') {
        const ip = userStates[chatId].ip;
        const subdomain = text;
        delete userStates[chatId]; // Clear the user's state

        const subdomainUrl = ${subdomain}.${DOMAIN};
        try {
            const response = await createSubdomain(ip, subdomain);
            if (response.success) {
                const successMessage = ✅ Subdomain created successfully!\n🌐 ${subdomainUrl};
                return sendTelegramMessage(chatId, successMessage);
            } else {
                const errorMessage = ❌ Failed to create subdomain: ${subdomainUrl}\n🔄 It might already exist.;
                return sendTelegramMessage(chatId, errorMessage);
            }
        } catch (error) {
            const errorMessage = 🚫 Error creating subdomain. Please try again later.;
            return sendTelegramMessage(chatId, errorMessage);
        }
    }

    return new Response('Command not recognized', { status: 400 });
}

// Function to create a subdomain on Cloudflare
async function createSubdomain(ip, subdomain) {
    const url = https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records;
    const data = {
        type: 'A',
        name: ${subdomain}.${DOMAIN},
        content: ip,
        ttl: 1,
        proxied: false
    };
    
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Auth-Email': EMAIL,
            'X-Auth-Key': API_KEY
        },
        body: JSON.stringify(data)
    });
    return await response.json();
}

// Function to send a message back to Telegram
async function sendTelegramMessage(chatId, text) {
    const url = ${TELEGRAM_API_URL}?chat_id=${chatId}&text=${encodeURIComponent(text)};
    await fetch(url);
}

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request));
})
