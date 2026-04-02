import mongoose from 'mongoose';

const VisitorSchema = new mongoose.Schema({
    ip: { type: String, unique: true, required: true },
    device: { type: String, default: 'Unknown' },
    timestamp: { type: Date, default: Date.now }
});

// TTL Trigger: Delete records after 90 days (7,776,000 seconds)
VisitorSchema.index({ timestamp: 1 }, { expireAfterSeconds: 7776000 });

const Visitor = mongoose.model('Visitor', VisitorSchema);
export default Visitor;
