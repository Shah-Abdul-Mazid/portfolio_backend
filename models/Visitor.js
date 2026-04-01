import mongoose from 'mongoose';

const VisitorSchema = new mongoose.Schema({
    ip: { type: String, unique: true, required: true },
    device: { type: String, default: 'Unknown' },
    timestamp: { type: Date, default: Date.now }
});

const Visitor = mongoose.model('Visitor', VisitorSchema);
export default Visitor;
