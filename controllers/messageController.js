import Message from '../models/Message.js';
import { sendAutoReply } from '../utils/emailjs.js';

export const postMessage = async (req, res) => {
    console.log('📩 Incoming message request:', req.body);
    try {
        const newMessage = new Message(req.body);
        const savedMessage = await newMessage.save();
        console.log('✅ Message saved to MongoDB:', savedMessage._id);
        
        // Trigger emails in background (non-blocking) so the UI doesn't hang
        sendAutoReply(req.body.email, req.body.name, req.body.phone, req.body.query)
            .then(() => console.log('Background email process finished.'))
            .catch(console.error);
        
        res.status(201).json(savedMessage);
    } catch (err) {
        console.error('Error saving message:', err.message);
        res.status(500).json({ error: 'Failed to save message' });
    }
};

export const getMessages = async (req, res) => {
    try {
        const messages = await Message.find().sort({ created_at: -1 });
        res.json(messages);
    } catch (err) {
        console.error('Error fetching messages:', err.message);
        res.status(500).json({ error: 'Failed to fetch messages' });
    }
};

export const deleteMessage = async (req, res) => {
    try {
        await Message.findByIdAndDelete(req.params.id);
        res.status(204).send();
    } catch (err) {
        console.error('Error deleting message:', err.message);
        res.status(500).json({ error: 'Failed to delete message' });
    }
};
