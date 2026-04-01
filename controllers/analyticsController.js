import Analytics from '../models/Analytics.js';
import Visitor from '../models/Visitor.js';

export const trackPageView = async (req, res) => {
    try {
        const ip = req.headers['x-forwarded-for']?.split(',')[0] || 
                   req.headers['x-real-ip'] || 
                   req.socket.remoteAddress || 
                   req.ip;

        const device = req.headers['user-agent'] || 'Unknown Device';

        if (!ip) throw new Error('Could not identify visitor IP');

        const existingVisit = await Visitor.findOne({ ip });

        if (!existingVisit) {
            await Visitor.create({ ip, device });
            const result = await Analytics.findOneAndUpdate(
                { id: 'total_views' },
                { $inc: { count: 1 } },
                { upsert: true, new: true }
            );
            return res.status(201).json(result);
        }

        const currentStats = await Analytics.findOne({ id: 'total_views' });
        res.json(currentStats || { count: 0 });
    } catch (err) {
        console.error('Error tracking visit:', err.message);
        res.status(500).json({ error: 'Failed to track visit' });
    }
};

export const getAnalytics = async (req, res) => {
    try {
        const result = await Analytics.findOne({ id: 'total_views' });
        res.json(result || { count: 0 });
    } catch (err) {
        console.error('Error fetching analytics:', err.message);
        res.status(500).json({ error: 'Failed to fetch analytics' });
    }
};

export const getVisitorsList = async (req, res) => {
    try {
        const visitors = await Visitor.find().sort({ timestamp: -1 });
        res.json(visitors);
    } catch (err) {
        console.error('Error fetching visitors:', err.message);
        res.status(500).json({ error: 'Failed to retrieve visitor log' });
    }
};

export const clearAllVisitors = async (req, res) => {
    try {
        await Visitor.deleteMany({});
        await Analytics.findOneAndUpdate({ id: 'total_views' }, { count: 0 });
        res.json({ success: true, message: 'All visitor records and view counts cleared.' });
    } catch (err) {
        console.error('Error clearing visitors:', err.message);
        res.status(500).json({ error: 'Failed to clear data' });
    }
};
