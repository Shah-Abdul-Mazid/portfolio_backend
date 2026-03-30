import PortfolioContent from '../models/PortfolioContent.js';

export const getPortfolioData = async (req, res) => {
    try {
        const doc = await PortfolioContent.findOne({ key: 'main' });
        if (!doc) return res.json(null);
        res.json(doc.data);
    } catch (err) {
        console.error('Error fetching portfolio data:', err.message);
        res.status(500).json({ error: 'Failed to fetch portfolio data' });
    }
};

export const savePortfolioData = async (req, res) => {
    try {
        const doc = await PortfolioContent.findOneAndUpdate(
            { key: 'main' },
            { data: req.body, updated_at: new Date() },
            { upsert: true, new: true }
        );
        console.log('✅ Portfolio data saved to MongoDB');
        res.json({ success: true, updated_at: doc.updated_at });
    } catch (err) {
        console.error('Error saving portfolio data:', err.message);
        res.status(500).json({ error: 'Failed to save portfolio data' });
    }
};
