import Message from '../models/Message.js';
import { sendAutoReply } from '../utils/emailjs.js';

// --- LOCAL MOCK STORAGE FOR VERIFICATION ---
let mockMessages = [];

export const postMessage = async (req, res) => {
    console.log('📩 Incoming message request:', req.body);
    try {
        // Attempt real DB save
        let savedMessage;
        try {
            const newMessage = new Message(req.body);
            savedMessage = await newMessage.save();
        } catch (dbErr) {
            console.warn('⚠️ DB Connection failed, using Local Mock Trigger for 30s test.');
            savedMessage = { 
                _id: 'mock-' + Date.now(), 
                ...req.body, 
                created_at: new Date().toISOString() 
            };
        }

        // Add to local mock list for the 30-sec expiration test
        mockMessages.push(savedMessage);
        console.log(`✅ Message active in local memory: ${savedMessage._id}`);

        // TRIGGER THE 30-SECOND EXPIRATION (Local Simulation)
        setTimeout(() => {
            mockMessages = mockMessages.filter(m => m._id !== savedMessage._id);
            console.log(`🔥 [TRIGGER] Message ${savedMessage._id} expired & deleted after 30 seconds.`);
        }, 30000);

        // Trigger emails in background
        sendAutoReply(req.body.email, req.body.name, req.body.phone, req.body.query)
            .then(() => console.log('Background email process finished.'))
            .catch(console.error);
        
        res.status(201).json(savedMessage);
    } catch (err) {
        console.error('Error in postMessage:', err.message);
        res.status(500).json({ error: 'Failed to process message' });
    }
};

export const getMessages = async (req, res) => {
    try {
        // Try real DB first
        let messages = [];
        try {
            messages = await Message.find().sort({ created_at: -1 });
        } catch (e) {
            messages = [...mockMessages];
        }
        res.json(messages);
    } catch (err) {
        console.error('Error fetching messages:', err.message);
        res.status(500).json({ error: 'Failed to fetch messages' });
    }
};

export const deleteMessage = async (req, res) => {
    try {
        const id = req.params.id;
        try {
            await Message.findByIdAndDelete(id);
        } catch (e) {}
        
        mockMessages = mockMessages.filter(m => m._id !== id);
        res.status(204).send();
    } catch (err) {
        console.error('Error deleting message:', err.message);
        res.status(500).json({ error: 'Failed to delete message' });
    }
};
