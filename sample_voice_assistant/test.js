/**
 * Smoke test for sample voice assistant codebase
 */
const voiceDispatcher = require('./agents/voice_dispatcher');
const { INTENTS } = require('./config/constants');

async function runSmokeTest() {
    console.log('Testing voice dispatcher intent routing...');
    const result = await voiceDispatcher.dispatchVoiceIntent(INTENTS.BLUETOOTH_OPEN_SETTINGS);
    console.log('Dispatch result:', result);
    console.log('All sample voice assistant modules loaded successfully!');
}

runSmokeTest().catch(console.error);
