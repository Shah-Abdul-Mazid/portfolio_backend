import mongoose from 'mongoose';

const AnalyticsSchema = new mongoose.Schema({
    id: { type: String, unique: true, required: true },
    count: { type: Number, default: 0 }
});

const Analytics = mongoose.model('Analytics', AnalyticsSchema);
export default Analytics;
