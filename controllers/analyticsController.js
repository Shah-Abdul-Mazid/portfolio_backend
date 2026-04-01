import Analytics from '../models/Analytics.js';
import Visitor from '../models/Visitor.js';

export const trackPageView = async (req, res) => {
    try {
        // Advanced IP detection (handling proxies/Vercel)
        const ip = req.headers['x-forwarded-for']?.split(',')[0] || 
                   req.headers['x-real-ip'] || 
                   req.socket.remoteAddress || 
                   req.ip;

        if (!ip) throw new Error('Could not identify visitor IP');

        // Check if this IP has visited before
        const existingVisit = await Visitor.findOne({ ip });

        if (!existingVisit) {
            // New unique visitor - Create record and increment total count
            await Visitor.create({ ip });
            const result = await Analytics.findOneAndUpdate(
                { id: 'total_views' },
                { $inc: { count: 1 } },
                { upsert: true, new: true }
            );
            return res.json(result);
        }

        // Return existing count if already exists
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
