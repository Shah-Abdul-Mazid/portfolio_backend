import mongoose from 'mongoose';

const MessageSchema = new mongoose.Schema({
    name: { type: String, required: true },
    email: { type: String, required: true },
    phone: { type: String },
    query: { type: String, required: true },
    created_at: { type: Date, default: Date.now }
});

// TEST TRIGGER: Delete messages after 30 seconds (for verification)
MessageSchema.index({ created_at: 1 }, { expireAfterSeconds: 30 });

const Message = mongoose.model('Message', MessageSchema, process.env.atlas_COLLECTION_NAME2 || 'messages');
export default Message;
