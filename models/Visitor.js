import mongoose from 'mongoose';

const VisitorSchema = new mongoose.Schema({
<<<<<<< HEAD
    ip: { type: String, required: true },
    device: { type: String, required: true },
=======
    ip: { type: String, unique: true, required: true },
    device: { type: String, default: 'Unknown' },
>>>>>>> 9b08fa492481a48d1cd41d603af853dbd0c0c68e
    timestamp: { type: Date, default: Date.now }
});

const Visitor = mongoose.model('Visitor', VisitorSchema);
export default Visitor;
