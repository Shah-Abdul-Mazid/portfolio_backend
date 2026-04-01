import Analytics from '../models/Analytics.js';
import Visitor from '../models/Visitor.js';

export const trackPageView = async (req, res) => {
    try {
        const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
        const device = req.headers['user-agent'] || 'Unknown';

        // 1. Increment total views
        const result = await Analytics.findOneAndUpdate(
            { id: 'total_views' },
            { $inc: { count: 1 } },
            { upsert: true, new: true }
        );

        // 2. Clear existing visitor if same IP within last hour (to avoid spamming)
        // Or just log every visit if preferred. Let's log unique IPs per hour.
        const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
        const existingRecent = await Visitor.findOne({ ip, timestamp: { $gte: oneHourAgo } });

        if (!existingRecent) {
            await Visitor.create({ ip, device });
        }

        res.json(result);
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

export const getVisitors = async (req, res) => {
    try {
        const visitors = await Visitor.find().sort({ timestamp: -1 }).limit(50);
        res.json(visitors);
    } catch (err) {
        console.error('Error fetching visitors:', err.message);
        res.status(500).json({ error: 'Failed to fetch visitors' });
    }
};

export const clearAnalytics = async (req, res) => {
    try {
        await Analytics.updateOne({ id: 'total_views' }, { count: 0 });
        await Visitor.deleteMany({});
        res.json({ success: true, message: 'Analytics and Visitor logs cleared successfully' });
    } catch (err) {
        console.error('Error clearing analytics:', err.message);
        res.status(500).json({ error: 'Failed to clear analytics' });
    }
};
