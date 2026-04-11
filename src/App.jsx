import React, { useState, useEffect, useRef } from 'react';
import {
  User, ChevronRight, ArrowLeft, Languages, Headphones, MonitorPlay,
  ArrowUp, ArrowDown, Minus, TrendingUp, TrendingDown,
  BrainCircuit, GraduationCap, Briefcase, Globe,
  Rocket, Lightbulb, CheckCircle2, XCircle, LogOut,
  MapPin, CloudSun, Calendar
} from 'lucide-react';
import './App.css';

const MARKET_DATA = [
  { symbol: 'NIFTY 50', value: '22,450.30', change: '+1.2%', up: true },
  { symbol: 'SENSEX', value: '74,100.15', change: '+1.1%', up: true },
  { symbol: 'Gold', value: '₹65,000', change: '-0.3%', up: false },
  { symbol: 'USD/INR', value: '83.25', change: '+0.1%', up: true },
  { symbol: 'Brent Oil', value: '$85.40', change: '+2.4%', up: true },
  { symbol: 'NASDAQ', value: '16,200', change: '+1.5%', up: true }
];

const NEWS_DATA = [
  {
    id: 'a0000000-0000-0000-0000-000000000001',
    category: 'Global Trends',
    title: 'Middle East Conflict Impacts Global Trade Routes',
    hindiTitle: 'मध्य पूर्व संघर्ष का वैश्विक व्यापार पर प्रभाव',
    marathiTitle: 'मध्य पूर्व संघर्षामुळे जागतिक व्यापारावर परिणाम',
    summary: 'Rising tensions disrupt major shipping lanes, affecting logistics and global supply chains.',
    hindiSummary: 'बढ़ते तनाव से प्रमुख शिपिंग मार्ग बाधित हो रहे हैं।',
    marathiSummary: 'वाढत्या तणावामुळे प्रमुख शिपिंग मार्ग विस्कळीत.',
    image: 'https://images.unsplash.com/photo-1581093458791-9f3c3900df4b?auto=format&fit=crop&w=600&h=400&q=80',
    audioSrc: { en: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3', hi: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3' },
    videoSrc: 'https://assets.mixkit.co/videos/preview/mixkit-animation-of-futuristic-devices-and-a-robot-3142-large.mp4',
    isImportant: true,
    impactChain: [
      { text: 'Conflict', hindiText: 'संघर्ष', marathiText: 'संघर्ष', direction: 'neutral' },
      { text: 'Supply Chain', hindiText: 'आपूर्ति', marathiText: 'पुरवठा साखळी', direction: 'down' },
      { text: 'Logistics Cost', hindiText: 'रसद लागत', marathiText: 'रसद खर्च', direction: 'up' },
      { text: 'Commodity Prices', hindiText: 'कीमतें', marathiText: 'किंमती', direction: 'up' }
    ],
    personalImpact: {
      student: [
        { en: 'International travel costs may increase', hi: 'अंतरराष्ट्रीय यात्रा की लागत बढ़ सकती है' },
        { en: 'Imported gadgets could get pricier', hi: 'आयातित गैजेट महंगे हो सकते हैं' }
      ],
      investor: [
        { en: 'Shipping & logistics stocks may see volatility', hi: 'शिपिंग और रसद शेयरों में अस्थिरता' },
        { en: 'Energy sector might experience temporary gains', hi: 'ऊर्जा क्षेत्र में अस्थायी लाभ' }
      ],
      general: [
        { en: 'Possible delay in imported goods delivery', hi: 'आयातित माल की डिलीवरी में देरी संभव' },
        { en: 'Household grocery prices might see marginal hike', hi: 'घरेलू किराने की कीमतों में मामूली बढ़ोतरी' }
      ],
      youngExplorer: [
        { en: 'Ships have to take a longer route, like a detour!', hi: 'जहाजों को लंबा रास्ता तय करना पड़ता है!' }
      ]
    },
    whatToDo: {
      student: [{ en: 'Explore opportunities in supply chain tech', hi: 'सप्लाई चेन टेक में अवसर तलाशें' }],
      investor: [{ en: 'Review exposure to import-heavy sectors', hi: 'आयात-निर्भर क्षेत्रों के निवेश की समीक्षा करें' }],
      general: [{ en: 'Plan major device purchases accordingly', hi: 'प्रमुख उपकरणों की खरीदारी की योजना बनाएं' }],
      youngExplorer: [{ en: 'Look at a world map to see ocean routes!', hi: 'समुद्र के रास्ते देखने के लिए दुनिया का नक्शा देखें!' }]
    },
    watchNext: [{ en: 'Suez Canal traffic reports', hi: 'स्वेज़ नहर यातायात रिपोर्ट' }],
    confidence: { en: 'Medium', hi: 'मध्यम' },
    disclaimer: { en: 'Based on historical maritime patterns.', hi: 'ऐतिहासिक समुद्री पैटर्न पर आधारित।' },
    didYouKnow: { en: 'About 90% of everything we buy travels by ship!', hi: 'हम जो कुछ भी खरीदते हैं उसका 90% जहाज से आता है!' },
    quiz: {
      question: { en: 'Most global goods are transported via:', hi: 'विदेशी माल ज्यादातर किससे लाया जाता है?' },
      options: [
        { en: 'Airplanes', hi: 'हवाई जहाज' },
        { en: 'Ships', hi: 'जहाज़' },
        { en: 'Trains', hi: 'ट्रेन' }
      ],
      answerIndex: 1
    }
  },
  {
    id: 'a0000000-0000-0000-0000-000000000002',
    category: 'AI & Future',
    title: 'Generative AI Accelerates Tech Automation',
    hindiTitle: 'जेनरेटिव एआई ने टेक ऑटोमेशन को गति दी',
    marathiTitle: 'जनरेटिव्ह एआय मुळे टेक ऑटोमेशनमध्ये गती',
    summary: 'New AI models are fundamentally shifting how code and daily tasks are executed.',
    hindiSummary: 'नए एआई मॉडल कोड और दैनिक कार्यों के निष्पादन के तरीके को बदल रहे हैं।',
    marathiSummary: 'नवीन एआय मॉडेल्स काम करण्याच्या पद्धतीत बदल करत आहेत.',
    image: 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=600&h=400&q=80',
    audioSrc: '',
    videoSrc: '',
    isImportant: true,
    impactChain: [
      { text: 'AI Adoption', hindiText: 'AI अपनाना', marathiText: 'AI चा अवलंब', direction: 'up' },
      { text: 'Routine Tasks', hindiText: 'नियमित कार्य', marathiText: 'नियमित कामे', direction: 'down' },
      { text: 'Company Margins', hindiText: 'कंपनी मार्जिन', marathiText: 'कंपनी मार्जिन', direction: 'up' },
      { text: 'New Job Roles', hindiText: 'नई नौकरियाँ', marathiText: 'नवीन नोकऱ्या', direction: 'up' }
    ],
    personalImpact: {
      student: [
        { en: 'AI literacy becomes a core hiring requirement', hi: 'एआई साक्षरता मुख्य भर्ती आवश्यकता' }
      ],
      investor: [
        { en: 'Software service margins likely to improve', hi: 'सॉफ्टवेयर सेवा मार्जिन में सुधार की संभावना' },
        { en: 'Cloud infrastructure demand surging', hi: 'क्लाउड इंफ्रास्ट्रक्चर की मांग में वृद्धि' }
      ],
      general: [
        { en: 'Opportunities to utilize AI for daily productivity', hi: 'दैनिक उत्पादकता के लिए एआई का उपयोग' }
      ],
      youngExplorer: [
        { en: 'Computers are learning to draw and write stories!', hi: 'कंप्यूटर चित्र बनाना और कहानियाँ लिखना सीख रहे हैं!' }
      ]
    },
    whatToDo: {
      student: [{ en: 'Focus on prompt engineering and logic', hi: 'प्रॉम्प्ट इंजीनियरिंग पर ध्यान दें' }],
      investor: [{ en: 'Identify leaders in AI hardware', hi: 'एआई हार्डवेयर लीडर्स की पहचान करें' }],
      general: [{ en: 'Try out fundamental AI writing tools', hi: 'बुनियादी एआई टूल्स का प्रयास करें' }],
      youngExplorer: [{ en: 'Ask a teacher how AI can help you study!', hi: 'शिक्षक से पूछें कि एआई कैसे मदद kar sakta hai!' }]
    },
    watchNext: [{ en: 'Enterprise adoption metrics', hi: 'उद्यम निगम मेट्रिक्स' }],
    confidence: { en: 'High', hi: 'उच्च' },
    disclaimer: { en: 'Based on corporate investment patterns.', hi: 'कॉर्पोरेट निवेश पैटर्न पर आधारित।' },
    didYouKnow: { en: 'The concept of AI was born over 60 years ago in 1956!', hi: 'एआई की अवधारणा 1956 में पैदा हुई थी!' },
    quiz: {
      question: { en: 'What is a popular use of modern Generative AI?', hi: 'आधुनिक जेनरेटिव एआई का एक लोकप्रिय उपयोग क्या है?' },
      options: [
        { en: 'Cooking food', hi: 'खाना बनाना' },
        { en: 'Creating text and images', hi: 'टेक्स्ट और चित्र बनाना' },
        { en: 'Driving trains', hi: 'ट्रेन चलाना' }
      ],
      answerIndex: 1
    }
  },
  {
    id: 'a0000000-0000-0000-0000-000000000003',
    category: 'Science',
    title: 'New Robotic Rover Detects Subsurface Mars Ice',
    hindiTitle: 'रोवर ने मंगल पर बर्फ की खोज की',
    marathiTitle: 'रोव्हरला मंगळावर बर्फ सापडला',
    summary: 'A breakthrough discovery of pristine water ice could fuel future manned missions.',
    hindiSummary: 'स्वच्छ पानी की बर्फ की खोज भविष्य के मानव मिशन को ऊर्जा दे सकती है।',
    marathiSummary: 'पाण्याची बर्फाची शोध भविष्यातील मानवी मिशनला चालना देऊ शकते.',
    image: 'https://images.unsplash.com/photo-1614730321146-b6fa6a46bcb4?auto=format&fit=crop&w=600&h=400&q=80',
    audioSrc: '',
    videoSrc: '',
    isImportant: false,
    impactChain: [
      { text: 'Mars Discovery', hindiText: 'मंगल ग्रह की खोज', marathiText: 'मंगळ शोध', direction: 'up' },
      { text: 'Space Funding', hindiText: 'अंतरिक्ष अनुसंधान निधि', marathiText: 'अंतराळ निधी', direction: 'up' },
      { text: 'Future Missions', hindiText: 'भविष्य के मिशन', marathiText: 'भविष्यातील मिशन्स', direction: 'up' }
    ],
    personalImpact: {
      student: [{ en: 'Expected surge in astrophysics scholarships', hi: 'खगोल विज्ञान छात्रवृत्ति में वृद्धि' }],
      investor: [{ en: 'Private space sector gains momentum', hi: 'निजी अंतरिक्ष क्षेत्र को गति' }],
      general: [{ en: 'A step closer to multi-planetary existence', hi: 'बहु-ग्रहीय अस्तित्व के करीब' }],
      youngExplorer: [{ en: 'Astronauts might use this ice for drinking water!', hi: 'अंतरिक्ष यात्री इस बर्फ का उपयोग पीने के लिए कर सकते हैं!' }]
    },
    whatToDo: {
      student: [{ en: 'Join space science communities', hi: 'अंतरिक्ष विज्ञान समुदायों में शामिल हों' }],
      investor: [{ en: 'Evaluate space-tech ETFs', hi: 'स्पेस-टेक ईटीएफ का मूल्यांकन करें' }],
      general: [{ en: 'Watch latest space documentaries', hi: 'अंतरिक्ष वृत्तचित्र देखें' }],
      youngExplorer: [{ en: 'Learn about the solar system tonight!', hi: 'आज रात सौर मंडल के बारे में जानें!' }]
    },
    watchNext: [{ en: 'Upcoming lunar launches', hi: 'आगामी चंद्र प्रक्षेपण' }],
    confidence: { en: 'Very High', hi: 'बहुत उच्च' },
    disclaimer: { en: 'Facts verified by official space agencies.', hi: 'आधिकारिक एजेंसियों द्वारा सत्यापित तथ्य।' },
    didYouKnow: { en: 'Mars is red because its surface is covered in iron oxide (rust)!', hi: 'मंगल लाल है क्योंकि इसकी सतह जंग (लोहे के आक्साइड) से ढकी है!' },
    quiz: {
      question: { en: 'Which planet is known as the Red Planet?', hi: 'किस ग्रह को लाल ग्रह के नाम से जाना जाता है?' },
      options: [
        { en: 'Venus', hi: 'शुक्र' },
        { en: 'Jupiter', hi: 'बृहस्पति' },
        { en: 'Mars', hi: 'मंगल' }
      ],
      answerIndex: 2
    }
  },
  {
    id: 'a0000000-0000-0000-0000-000000000004',
    category: 'Economy',
    title: 'Central Bank Maintains Interest Rates for Q3',
    hindiTitle: 'केंद्रीय बैंक ने ब्याज दरों को स्थिर रखा',
    summary: 'The decision aims to balance inflation control with steady economic growth.',
    image: 'https://images.unsplash.com/photo-1611974717483-5828ff797ae1?auto=format&fit=crop&w=600&h=400&q=80',
    isImportant: true,
    impactChain: [{ text: 'Market Stability', direction: 'up' }],
    personalImpact: {
      investor: [{ en: 'Borrowing costs remain predictable for businesses', hi: 'व्यवसायों के लिए ऋण लागत अनुमानित बनी हुई है' }],
      student: [{ en: 'Education loan rates stable for current semester', hi: 'शिक्षा ऋण दरें स्थिर' }],
      general: [{ en: 'Housing mortgage payments unlikely to spike soon', hi: 'बंधक भुगतान में वृद्धि की संभावना नहीं' }]
    },
    whatToDo: { investor: [{ en: 'Assess bond yields vs equity risks', hi: 'बॉन्ड यील्ड और इक्विटी रिस्क का आकलन करें' }] }
  },
  {
    id: 'a0000000-0000-0000-0000-000000000005',
    category: 'Education',
    title: 'New Global Scholarship Program for AI Research',
    hindiTitle: 'एआई रिसर्च के लिए नया वैश्विक छात्रवृत्ति कार्यक्रम',
    summary: 'Top universities partner to fund 500 doctoral candidates in machine learning.',
    image: 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=600&h=400&q=80',
    isImportant: false,
    impactChain: [{ text: 'Academic Growth', direction: 'up' }],
    personalImpact: {
      student: [{ en: 'Huge opportunity for final year tech students', hi: 'अंतिम वर्ष के तकनीकी छात्रों के लिए बड़ा अवसर' }],
      general: [{ en: 'More research leads to better consumer AI tools', hi: 'बेहतर उपभोक्ता एआई विकास' }]
    },
    whatToDo: { student: [{ en: 'Check eligibility criteria on official portal', hi: 'आधिकारिक पोर्टल पर पात्रता मानदंड देखें' }] }
  }
];

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('landing');
  const [profile, setProfile] = useState(null);
  const [selectedArticleId, setSelectedArticleId] = useState(null);
  const [lang, setLang] = useState('en');
  const [articles, setArticles] = useState(NEWS_DATA);

  useEffect(() => {
    // Fetch initial feed from DB
    fetch('http://localhost:8001/api/feed')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success' && data.articles && data.articles.length > 0) {
          const mappedArticles = data.articles.map((a, idx) => ({
             id: a.id,
             category: a.category || 'Global Trends',
             title: a.title,
             hindiTitle: a.title,
             marathiTitle: a.title,
             summary: a.source || 'Breaking News',
             hindiSummary: a.source || 'Breaking News',
             marathiSummary: a.source || 'Breaking News',
             image: a.image_url || a.thumbnail || 'https://images.unsplash.com/photo-1581093458791-9f3c3900df4b?auto=format&fit=crop&w=600&h=400&q=80',
             url: a.url,
             isImportant: idx < 2
          }));
          setArticles(mappedArticles);
        }
      })
      .catch(err => console.error("Error fetching feed:", err));

    // Load stored user data
    const savedUser = localStorage.getItem('insightx_user');
    if (savedUser) {
      const userData = JSON.parse(savedUser);
      setProfile(userData.role);
    }

    const handleHash = () => {
      const hash = window.location.hash.slice(1);
      if (['landing', 'profile', 'feed', 'insight'].includes(hash)) {
        setCurrentScreen(hash);
      } else {
        const initialScreen = savedUser ? 'feed' : 'landing';
        window.location.hash = initialScreen;
        setCurrentScreen(initialScreen);
      }
    };

    if (!window.location.hash) {
      window.location.hash = savedUser ? 'feed' : 'landing';
    } else {
      handleHash();
    }

    const onHashChange = () => handleHash();
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const navigate = (screen) => {
    window.location.hash = screen;
    setCurrentScreen(screen);
    window.scrollTo(0, 0);
  };

  const handleOnboardingComplete = (userData) => {
    // Save to local state and localStorage
    setProfile(userData.role);
    localStorage.setItem('insightx_user', JSON.stringify(userData));
    navigate('feed');
  };

  const handleProfileSelect = (selectedProfile) => {
    setProfile(selectedProfile);
    navigate('feed');
  };

  const handleArticleSelect = (articleId) => {
    setSelectedArticleId(articleId);
    navigate('insight');
  };

  return (
    <div className="app-container">
      {currentScreen === 'landing' && (
        <LandingScreen onEnter={() => navigate('profile')} lang={lang} />
      )}
      {currentScreen === 'profile' && (
        <OnboardingScreen onComplete={handleOnboardingComplete} lang={lang} />
      )}
      {currentScreen === 'feed' && (
        <FeedScreen
          articles={articles}
          profile={profile}
          lang={lang}
          onProfileClick={() => navigate('profile')}
          onArticleClick={handleArticleSelect}
        />
      )}
      {currentScreen === 'insight' && (
        <InsightScreen
          articleId={selectedArticleId}
          articles={articles}
          profile={profile}
          lang={lang}
          setLang={setLang}
          onBack={() => navigate('feed')}
        />
      )}
    </div>
  );
}

function LandingScreen({ onEnter, lang }) {
  return (
    <div className="fade-in flex flex-col items-center justify-center p-4" style={{ minHeight: '100vh', background: 'var(--bg-color)' }}>
      <div style={{ textAlign: 'center', marginBottom: '4rem', maxWidth: '600px' }}>
        <h1 style={{ fontSize: '3.5rem', fontWeight: '800', letterSpacing: '-1px', marginBottom: '1rem' }}>
          InsightX <span style={{ color: 'var(--accent-color)' }}>AI</span>
        </h1>
        <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', fontFamily: 'var(--font-modern)' }}>
          {lang === 'en' ? 'Understand the World Around You' : 'अपने आस-पास की दुनिया को समझें'}
        </p>
      </div>

      <button
        onClick={onEnter}
        style={{
          background: 'var(--primary-color)',
          color: 'white',
          padding: '1rem 3rem',
          fontSize: '1.125rem',
          fontFamily: 'var(--font-modern)',
          fontWeight: '600',
          border: 'none',
          borderRadius: '100px',
          cursor: 'pointer',
          boxShadow: '0 4px 15px rgba(15, 23, 42, 0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          transition: 'transform 0.2s, box-shadow 0.2s',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 6px 20px rgba(15, 23, 42, 0.3)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 4px 15px rgba(15, 23, 42, 0.2)';
        }}
      >
        {lang === 'en' ? 'Enter Platform' : 'शुरू करें'}
        <ChevronRight size={20} />
      </button>
    </div>
  );
}

function OnboardingScreen({ onComplete, lang }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'student',
    interests: []
  });
  const [interestInput, setInterestInput] = useState('');

  const suggestedInterests = ['AI', 'Technology', 'Finance', 'Space', 'Startups', 'Sports', 'Economy'];

  const profiles = [
    { id: 'student', title: lang === 'en' ? 'Student' : 'छात्र', icon: <GraduationCap size={20} /> },
    { id: 'investor', title: lang === 'en' ? 'Investor' : 'निवेशक', icon: <Briefcase size={20} /> },
    { id: 'general', title: lang === 'en' ? 'General' : 'सामान्‍य', icon: <Globe size={20} /> },
    { id: 'youngExplorer', title: lang === 'en' ? 'Young Explorer' : 'युवा खोजकर्ता', icon: <BrainCircuit size={20} /> },
  ];

  const addInterest = (interest) => {
    const trimmed = interest.trim();
    if (trimmed && !formData.interests.includes(trimmed)) {
      setFormData(prev => ({
        ...prev,
        interests: [...prev.interests, trimmed]
      }));
    }
    setInterestInput('');
  };

  const removeInterest = (interest) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.filter(i => i !== interest)
    }));
  };

  const isReturningUser = !!localStorage.getItem('insightx_user');

  const handleEnter = async () => {
    if (isReturningUser || (formData.name && formData.email)) {
      // Merge with existing data if any
      const existingUser = JSON.parse(localStorage.getItem('insightx_user') || '{}');
      const updatedUser = { ...existingUser, ...formData };
      
      // POST to backend ONLY if dealing with a new capture or updates
      try {
        const response = await fetch('http://localhost:8001/api/users/onboard', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedUser)
        });
        
        if (!response.ok) {
            console.error("Failed to sync user with backend");
            // we proceed gracefully via localstorage anyway for UX flow
        }
      } catch(e) {
          console.error("Backend unreachable", e);
      }
      
      onComplete(updatedUser);
    } else {
      alert('Please enter at least Name and Email');
    }
  };

  return (
    <div className="fade-in onboarding-container">
      <div className="onboarding-card">
        <h2 className="onboarding-title">
          {isReturningUser ? (lang === 'en' ? 'Choose Your Focus' : 'अपना फोकस चुनें') : (lang === 'en' ? 'Welcome to InsightX' : 'InsightX में आपका स्वागत है')}
        </h2>
        <p className="onboarding-subtitle">
          {isReturningUser ? (lang === 'en' ? 'Switch profile or update interests' : 'प्रोफ़ाइल बदलें या रुचियां अपडेट करें') : (lang === 'en' ? 'Let\'s personalize your experience' : 'आइए आपके अनुभव को वैयक्तिकृत करें')}
        </p>

        {!isReturningUser && (
          <>
            <div className="form-group">
              <label>{lang === 'en' ? 'Name' : 'नाम'}</label>
              <input
                type="text"
                placeholder={lang === 'en' ? 'Enter your name' : 'अपना नाम दर्ज करें'}
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label>{lang === 'en' ? 'Email' : 'ईमेल'}</label>
              <input
                type="email"
                placeholder={lang === 'en' ? 'Enter your email' : 'अपना ईमेल दर्ज करें'}
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </div>
          </>
        )}

        <div className="form-group">
          <label>{lang === 'en' ? 'Select Profile' : 'प्रोफ़ाइल चुनें'}</label>
          <div className="role-grid">
            {profiles.map(p => (
              <div
                key={p.id}
                className={`role-option ${formData.role === p.id ? 'active' : ''}`}
                onClick={() => setFormData({ ...formData, role: p.id })}
              >
                {p.icon}
                <span>{p.title}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>{lang === 'en' ? 'What are your interests?' : 'आपकी रुचियां क्या हैं?'}</label>
          <div className="tag-input-wrapper">
            <input
              type="text"
              placeholder={lang === 'en' ? 'Type and press Enter or +' : 'टाइप करें और Enter दबाएं'}
              value={interestInput}
              onChange={(e) => setInterestInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addInterest(interestInput)}
            />
            <button className="add-tag-btn" onClick={() => addInterest(interestInput)}>+</button>
          </div>

          <div className="suggested-interests">
            {suggestedInterests.map(interest => (
              <button
                key={interest}
                className="suggested-btn"
                onClick={() => addInterest(interest)}
                disabled={formData.interests.includes(interest)}
              >
                {interest}
              </button>
            ))}
          </div>

          <div className="interest-tags">
            {formData.interests.map(interest => (
              <span key={interest} className="interest-tag">
                {interest}
                <button onClick={() => removeInterest(interest)}>✕</button>
              </span>
            ))}
          </div>
        </div>

        <button className="enter-platform-btn" onClick={handleEnter}>
          {lang === 'en' ? 'Enter Platform' : 'प्लेटफ़ॉर्म में प्रवेश करें'}
          <ChevronRight size={18} />
        </button>
      </div>
    </div>
  );
}


function FeedScreen({ articles, profile, lang, onProfileClick, onArticleClick }) {
  const [activeCategory, setActiveCategory] = useState('All');
  const [subTab, setSubTab] = useState('top'); // 'top' or 'forYou'
  const [weather, setWeather] = useState({ temp: '30', city: 'Pune' });

  useEffect(() => {
    // 🛠️ Using environment variable for security
    const API_KEY = import.meta.env.VITE_OPENWEATHER_API_KEY; 
    const CITY = 'Pune'; 
    
    if (API_KEY) {
      fetch(`https://api.openweathermap.org/data/2.5/weather?q=${CITY}&units=metric&appid=${API_KEY}`)
        .then(res => res.json())
        .then(data => {
          if (data.main && data.name) {
            setWeather({
              temp: Math.round(data.main.temp),
              city: data.name
            });
          }
        })
        .catch(err => console.error("Weather fetch failed:", err));
    }
  }, []);

  const importantNews = NEWS_DATA.filter(n => n.isImportant);
  let feedNews = NEWS_DATA.filter(n => !n.isImportant);

  if (activeCategory !== 'All') {
    feedNews = NEWS_DATA.filter(n => n.category === activeCategory);
  }

  // Define forYouNews logic
  const userData = JSON.parse(localStorage.getItem('insightx_user') || '{}');
  const userInterests = userData.interests || [];
  const forYouNews = NEWS_DATA.filter(news => {
    // Priority 1: Match profile-specific content
    const hasProfileImpact = news.personalImpact && news.personalImpact[profile];

    // Priority 2: Match user interests (if any)
    const matchesInterest = userInterests.some(interest =>
      news.category.toLowerCase().includes(interest.toLowerCase()) ||
      news.title.toLowerCase().includes(interest.toLowerCase())
    );

    return hasProfileImpact || matchesInterest;
  });

  // Pre-defined categories
  const categories = ['All', 'Tech Innovation', 'AI & Future', 'Startups', 'Science', 'Global Trends', 'Sports', 'Entertainment', 'Lifestyle', 'Education', 'Economy', 'Careers', 'Politics'];

  const handleLogout = () => {
    localStorage.removeItem('insightx_user');
    window.location.hash = 'landing';
    window.location.reload(); // Hard reset for clean state
  };

  return (
    <div className="fade-in bg-white" style={{ minHeight: '100vh' }}>
      <header className="header">
        <div className="header-left">
          <div className="context-item">
            <MapPin size={14} />
            <span>{weather.city}, IN</span>
          </div>
          <div className="context-item divider">|</div>
          <div className="context-item">
            <Calendar size={14} />
            <span>{new Date().toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })}</span>
          </div>
          <div className="context-item divider">|</div>
          <div className="context-item">
            <CloudSun size={14} />
            <span>{weather.temp}°C</span>
          </div>
        </div>

        <div className="header-center">
          <div className="logo-text" onClick={() => window.location.hash = 'landing'} style={{ cursor: 'pointer' }}>
            InsightX <span>AI</span>
          </div>
          <div className="tagline">
            {profile === 'youngExplorer' ? (lang === 'en' ? 'Learn the World!' : 'दुनिया सीखें!') : (lang === 'en' ? 'Understand the World Around You' : 'दुनिया को समझें')}
          </div>
        </div>

        <div className="header-right">
          <button className="profile-icon" onClick={onProfileClick} title="Switch Profile">
            <User size={18} />
          </button>
          <button className="profile-icon logout-btn" onClick={handleLogout} title="Logout">
            <LogOut size={18} />
          </button>
        </div>
      </header>

      <div className="dashboard-layout">
        {/* 1️⃣ LEFT SIDEBAR: Quick Reads */}
        <aside className="sidebar left-sidebar">
          <div className="sidebar-header">
            <TrendingUp size={16} />
            <h2 className="sidebar-title">Quick Reads</h2>
          </div>
          <div className="sidebar-scroll no-scrollbar">
            {articles.map(news => (
              <div key={`quick-${news.id}`} className="quick-read-item" onClick={() => onArticleClick(news.id)}>
                <span className="quick-tag">{news.category}</span>
                <h4 className="quick-headline">{lang === 'en' ? news.title : news.hindiTitle}</h4>
              </div>
            ))}
          </div>
        </aside>

        {/* 2️⃣ CENTER MAIN FEED */}
        <main className="center-feed p-4">
          <div className="feed-container">
            {/* 🎯 Layout: Title -> Categories -> SubTabs -> Cards */}
            <div className="profile-header fade-in">
              <h1 className="profile-title">
                {profile === 'investor' ? 'Market Portfolio & Insights' :
                  profile === 'student' ? 'Academic & Campus Trends' :
                    profile === 'youngExplorer' ? 'Fun Stories & Discoveries' :
                      'Daily Digest & Global Updates'}
              </h1>
            </div>

            {/* Categories - Available for ALL profiles */}
            <div className="category-tabs fade-in">
              {categories.map(cat => (
                <button
                  key={cat}
                  className={`pill-btn ${activeCategory === cat ? 'active' : ''}`}
                  onClick={() => {
                    setActiveCategory(cat);
                    if (cat === 'All') setSubTab('top');
                  }}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Sub Tabs for "All" Category */}
            {activeCategory === 'All' && (
              <div className="sub-tabs-container fade-in">
                <button
                  className={`sub-tab ${subTab === 'top' ? 'tab-active active' : 'tab-inactive'}`}
                  onClick={() => setSubTab('top')}
                >
                  Top Stories
                </button>
                <button
                  className={`sub-tab ${subTab === 'forYou' ? 'tab-active active' : 'tab-inactive'}`}
                  onClick={() => setSubTab('forYou')}
                >
                  For You
                </button>
              </div>
            )}

            {/* Content rendering */}
            <div className="feed-content-area fade-in">
              {activeCategory === 'All' ? (
                subTab === 'top' ? (
                  /* Top Stories Tab */
                  <div className="news-grid-vertical">
                    {importantNews.map(news => (
                      <div
                        key={news.id}
                        className={`news-card-horizontal ${profile === 'youngExplorer' ? 'young-explorer-card' : ''}`}
                        onClick={() => onArticleClick(news.id)}
                      >
                        <div className="card-content">
                          <span className="category-tag-inline">{news.category}</span>
                          <h3 className="card-title">{lang === 'en' ? news.title : news.hindiTitle}</h3>
                          <p className="card-summary">{lang === 'en' ? news.summary : news.hindiSummary}</p>
                        </div>
                        {news.image && (
                          <div className="card-thumbnail-fixed">
                            <img src={news.image} alt="" className="news-image" />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  /* For You Tab */
                  <div className="news-grid-vertical">
                    {forYouNews.map(news => (
                      <div
                        key={`foryou-${news.id}`}
                        className={`news-card-horizontal ${profile === 'youngExplorer' ? 'young-explorer-card' : ''}`}
                        onClick={() => onArticleClick(news.id)}
                      >
                        <div className="card-content">
                          <span className="category-tag-inline">{news.category}</span>
                          <h3 className="card-title">{lang === 'en' ? news.title : news.hindiTitle}</h3>
                          <p className="card-summary">{lang === 'en' ? news.summary : news.hindiSummary}</p>
                        </div>
                        {news.image && (
                          <div className="card-thumbnail-fixed">
                            <img src={news.image} alt="" className="news-image" />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )
              ) : (
                /* Other Categories */
                <div className="news-grid-vertical">
                  {feedNews.map(news => (
                    <div
                      key={news.id}
                      className={`news-card-horizontal ${profile === 'youngExplorer' ? 'young-explorer-card' : ''}`}
                      onClick={() => onArticleClick(news.id)}
                    >
                      <div className="card-content">
                        <span className="category-tag-inline">{news.category}</span>
                        <h3 className="card-title">{lang === 'en' ? news.title : news.hindiTitle}</h3>
                        <p className="card-summary">{lang === 'en' ? news.summary : news.hindiSummary}</p>
                      </div>
                      {news.image && (
                        <div className="card-thumbnail-fixed">
                          <img src={news.image} alt="" className="news-image" />
                        </div>
                      )}
                    </div>
                  ))}
                  {feedNews.length === 0 && (
                    <p className="text-muted mt-2">No news found for this category.</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </main>

        {/* 3️⃣ RIGHT SIDEBAR: Visual Stories */}
        <aside className="sidebar right-sidebar">
          <div className="sidebar-header">
            <MonitorPlay size={16} />
            <h2 className="sidebar-title">Visual Stories</h2>
          </div>
          <div className="sidebar-scroll no-scrollbar">
            {articles.map(news => (
              <div key={`visual-${news.id}`} className="visual-story-card-overlay visual-card" onClick={() => onArticleClick(news.id)}>
                <img src={news.image} alt="" className="visual-bg" />
                <div className="visual-overlay">
                  <h4 className="visual-overlay-title">{lang === 'en' ? news.title : news.hindiTitle}</h4>
                </div>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}

function InsightScreen({ articleId, articles, profile, lang, setLang, onBack }) {
  const baseArticle = articles.find(n => n.id === articleId) || articles[0];
  const [article, setArticle] = React.useState(baseArticle);
  const [isLoading, setIsLoading] = React.useState(true);
  
  const [isPlaying, setIsPlaying] = React.useState(false);
  const [showVideo, setShowVideo] = React.useState(false);
  const [selectedOpt, setSelectedOpt] = React.useState(null);
  const [activeTab, setActiveTab] = React.useState('summary');

  React.useEffect(() => {
    if (!articleId) return;
    setIsLoading(true);
    fetch('http://localhost:8001/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ article_id: articleId, profile: profile || 'student' })
    })
    .then(res => res.json())
    .then(data => {
      if (data && data.profile_used) {
        // Map backend InsightOutput to frontend expected structure
        const nextStepsMapped = data.next_steps ? data.next_steps.map(step => ({ en: step, hi: step })) : [];
        const personalImpacts = data.profile_specific_insights ? Object.values(data.profile_specific_insights).filter(Boolean).map(val => ({ en: JSON.stringify(val), hi: JSON.stringify(val) })) : [];
        
        const mapped = {
          ...baseArticle,
          summary: data.summary || baseArticle.summary,
          hindiSummary: data.summary || baseArticle.hindiSummary,
          confidence: { en: data.fact_check_confidence, hi: data.fact_check_confidence },
          didYouKnow: { en: data.simplified_explainer || '', hi: data.simplified_explainer || '' },
          impactChain: data.cause_effect ? Object.keys(data.cause_effect).map(k => ({ text: k, direction: 'up' })) : [{ text: data.sentiment_label, direction: data.sentiment_label === 'positive' ? 'up' : 'down' }],
          personalImpact: {
            [profile]: personalImpacts.length ? personalImpacts : [{ en: 'Analyzing impact...', hi: 'Analyzing impact...' }]
          },
          whatToDo: {
            [profile]: nextStepsMapped.length ? nextStepsMapped : [{ en: 'No immediate action required.', hi: 'No immediate action required.' }]
          },
          quiz: data.quiz && data.quiz.length > 0 ? {
            question: { en: data.quiz[0].question || '', hi: data.quiz[0].question || '' },
            options: (data.quiz[0].options || []).map(opt => ({ en: opt, hi: opt })),
            answerIndex: data.quiz[0].answer_index || 0
          } : null
        };
        setArticle(mapped);
      }
      setIsLoading(false);
    })
    .catch(err => {
      console.error(err);
      setIsLoading(false);
    });
  }, [articleId, profile]);

  if (isLoading) {
    return (
      <div className="fade-in bg-white insight-page-wrapper" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', flexDirection: 'column' }}>
         <h2 style={{color: 'var(--primary-color)'}}>AI Agents are analyzing this article...</h2>
         <p style={{color: 'var(--text-secondary)'}}>Extracting facts, checking sentiment, and personalizing insights for you.</p>
         <button onClick={onBack} style={{marginTop: '20px', padding: '10px 20px', borderRadius: '50px', background: 'var(--bg-secondary)', border: 'none', cursor: 'pointer'}}>Cancel</button>
      </div>
    );
  }

  const getLocalizedText = (obj) => {
    return lang === 'en' ? obj.en : (lang === 'hi' ? obj.hi : obj.marathi);
  };

  const getPropText = (obj, enKey, hiKey, mrKey) => {
    return lang === 'en' ? obj[enKey] : (lang === 'hi' ? obj[hiKey] : (obj[mrKey] || obj[hiKey]));
  };

  const renderDirectionIcon = (direction) => {
    switch (direction) {
      case 'up': return <ArrowUp size={24} className="text-accent" style={{ color: 'var(--accent-color)' }} />;
      case 'down': return <ArrowDown size={24} style={{ color: '#dc2626' }} />;
      default: return <Minus size={24} className="text-muted" />;
    }
  };

  const cycleLanguage = () => {
    setLang(prev => prev === 'en' ? 'hi' : 'en');
  };

  const toggleAudio = () => {
    if (isPlaying) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
    } else {
      const textToRead = lang === 'en' ? article.title : article.hindiTitle;
      const utterance = new SpeechSynthesisUtterance(textToRead);
      utterance.lang = lang === 'en' ? 'en-US' : 'hi-IN';
      utterance.onend = () => setIsPlaying(false);
      window.speechSynthesis.speak(utterance);
      setIsPlaying(true);
    }
  };

  return (
    <div className="fade-in bg-white insight-page-wrapper">
      <div className="immersive-container">
        <header className="insight-header">
          <button className="back-btn" onClick={onBack} aria-label="Go Back">
            <ArrowLeft size={20} /> <span>Back to Feed</span>
          </button>

          <div className="title-section">
            <h1 className="insight-hero-title">{getPropText(article, 'title', 'hindiTitle', 'marathiTitle')}</h1>
            <p className="insight-hero-subtitle">
              {getPropText(article, 'summary', 'hindiSummary', 'marathiSummary')}
            </p>
          </div>

          <div className="multimodal-actions">
            <button className="pill-action-btn" onClick={cycleLanguage}>
              <Languages size={18} />
              {lang === 'en' ? 'Translate to Hindi' : 'English में पढ़ें'}
            </button>
            <button className="pill-action-btn" onClick={toggleAudio}>
              <Headphones size={18} />
              {isPlaying ? (lang === 'en' ? 'Pause' : 'रोकें') : (lang === 'en' ? 'Listen' : 'सुनें')}
            </button>
            {article.videoSrc && (
              <button className="pill-action-btn" onClick={() => setShowVideo(!showVideo)}>
                <MonitorPlay size={18} />
                {lang === 'en' ? 'AI Video' : 'AI वीडियो'}
              </button>
            )}
          </div>
        </header>

        <div className="article-columns">
          <div className="article-main-col">
            {showVideo && article.videoSrc && (
              <div className="article-video-box">
                <video controls autoPlay loop>
                  <source src={article.videoSrc} type="video/mp4" />
                </video>
              </div>
            )}

            {!showVideo && article.image && (
              <div className="article-hero-image">
                <img src={article.image} alt="Hero" />
              </div>
            )}

            <div className="article-tabs">
              <button
                className={`article-tab ${activeTab === 'summary' ? 'active' : ''}`}
                onClick={() => setActiveTab('summary')}
              >
                Summary
              </button>
              <button
                className={`article-tab ${activeTab === 'full' ? 'active' : ''}`}
                onClick={() => setActiveTab('full')}
              >
                Full Article
              </button>
            </div>

            <div className="article-body-content">
              {activeTab === 'summary' ? (
                <div className="summary-view fade-in">
                  <div className="inline-image image-right">
                    <img src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=400&q=80" alt="Detail" />
                    <span className="caption">Contextual Visualization</span>
                  </div>
                  <p className="drop-cap">{getPropText(article, 'summary', 'hindiSummary', 'marathiSummary')}. {lang === 'en' ? 'This development marks a significant shift in the current landscape, bringing forth new opportunities and challenges for stakeholders. Experts suggest that we are entering a pivotal moment where technological and social forces converge.' : 'यह विकास वर्तमान परिदृश्य में एक महत्वपूर्ण बदलाव का संकेत देता है, जो हितधारकों के लिए नए अवसर और चुनौतियां लेकर आता है।'}</p>

                  <p>{lang === 'en' ? 'The underlying data reveals a steady progression towards broader infrastructure support and global integration. As markets react to these shifting dynamics, the impact is being felt across multiple sectors, reinforcing the need for adaptive strategies and intelligent forecasting.' : 'अंतर्निहित डेटा व्यापक बुनियादी ढांचे के समर्थन और वैश्विक एकीकरण की ओर निरंतर प्रगति को प्रकट करता है।'}</p>
                </div>
              ) : (
                <div className="full-view fade-in">
                  <div className="inline-image image-left">
                    <img src="https://images.unsplash.com/photo-1544006659-f0b21f04cb1b?auto=format&fit=crop&w=400&q=80" alt="Innovation" />
                    <span className="caption">Expert Analysis</span>
                  </div>
                  <p className="drop-cap">{lang === 'en' ? 'In an era defined by rapid transformation, the recent developments in our local and global systems present a compelling narrative of innovation and resilience. This extensive report underscores how fundamental shifts in resources and technology are reshaping established norms across the globe. As we delve deeper into the core drivers of this change, it becomes evident that the intersection of digital infrastructure and human ingenuity is at the forefront of the next economic cycle.' : 'तेजी से बदलाव के युग में, हमारी स्थानीय और वैश्विक प्रणालियों में हालिया घटनाक्रम नवाचार और लचीलेपन की एक सम्मोहक कहानी पेश करते हैं।'}</p>

                  <p>{lang === 'en' ? 'Detailed analysis from top-tier research institutions highlights the critical role of systematic integration. By aligning strategic goals with technological capabilities, organizations are finding new ways to drive growth while maintaining operational stability in uncertain times. The data suggests that companies adopting a "technology-first" mindset are outperforming their peers by a significant margin. This performance gap is expected to widen as AI-driven automation becomes the standard rather than the exception.' : 'शीर्ष शोध संस्थानों का विस्तृत विश्लेषण व्यवस्थित एकीकरण की महत्वपूर्ण भूमिका को उजागर करता है।'}</p>

                  <p>{lang === 'en' ? 'Furthermore, the social implications of these changes are becoming increasingly apparent. From educational transformations to shifting economic models, the ripple effects are pervasive, touching every aspect of modern life. Educational institutions are already beginning to pivot their curricula toward the skills of the future, focusing on high-level cognitive tasks that complement machine efficiency. This shift represents a fundamental rebranding of the workforce as we know it, with a premium placed on adaptability and lifelong learning.' : 'इसके अलावा, इन परिवर्तनों के सामाजिक प्रभाव तेजी से स्पष्ट होते जा रहे हैं।'}</p>

                  <p>{lang === 'en' ? 'Looking ahead, the long-term sustainability of these advancements will depend heavily on regulatory frameworks and ethical considerations. Policymakers are now tasked with the difficult challenge of fostering innovation while protecting public interests. Early indicators suggest a trend toward more unified global standards, which could significantly reduce friction in international trade and data exchange. As new data emerge daily, the ability to interpret and act on this information will be the primary differentiator for leaders in the coming decade.' : 'आगे बढ़ते हुए, इन प्रगतियों की दीर्घकालिक स्थिरता नियामक ढांचे और नैतिक विचारों पर निर्भर करेगी।'}</p>

                  <p>{lang === 'en' ? 'In conclusion, while the path forward presents its share of complexities, the opportunities for positive impact have never been greater. By embracing these shifts with a focus on collaborative problem-solving and ethical implementation, we can ensure that the benefits of this transformation are shared broadly across society. The key takeaway for stakeholders is clear: remain agile, stay informed, and prioritize inclusive growth in every strategic decision.' : 'अंत में, जबकि आगे का रास्ता अपनी जटिलताओं का हिस्सा प्रस्तुत करता है, सकारात्मक प्रभाव के अवसर कभी इतने महान नहीं रहे हैं।'}</p>
                </div>
              )}
            </div>
          </div>

          <aside className="article-right-col">
            <div className="sticky-panel">
              <div className="chain-header">
                <h2 className="chain-title">
                  {profile === 'youngExplorer' ? 'How It Works' : 'Chain Reaction'}
                </h2>
                <div className="impact-badge high">High Impact</div>
              </div>

              <div className="vertical-chain">
                {article.impactChain.map((node, i) => (
                  <div key={i} className="chain-node-card">
                    <div className={`chain-icon-box ${node.direction}`}>
                      {renderDirectionIcon(node.direction)}
                    </div>
                    <div className="chain-content-box">
                      <div className="chain-label">{lang === 'en' ? node.text : (node.hindiText || node.text)}</div>
                      <div className="chain-desc">{lang === 'en' ? 'Direct influence on market metrics' : 'बाजार मेट्रिक्स पर सीधा प्रभाव'}</div>
                    </div>
                  </div>
                ))}
              </div>

              {profile !== 'youngExplorer' && (
                <div className="watch-next-sidebar" style={{ marginTop: '2.5rem' }}>
                  <h3 className="chain-title" style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>
                    {lang === 'en' ? 'Watch Next' : 'आगे क्या देखना है'}
                  </h3>
                  <div className="flex flex-col gap-3">
                    {article.watchNext.map((watch, i) => (
                      <div key={i} className="chain-node-card" style={{ padding: '1rem', alignItems: 'center' }}>
                        <ChevronRight size={16} color="var(--accent-color)" />
                        <span className="font-medium text-sm">{getLocalizedText(watch)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </aside>
        </div>

        {/* 🔻 BELOW ARTICLE (FULL WIDTH) */}
        <div className="article-footer-sections">
          <div className="footer-grid">
            {/* Personal Impact */}
            <section className="footer-insight-card" style={{ marginBottom: 0 }}>
              <h2 className="footer-section-title">
                {profile === 'youngExplorer' ? 'Why It Matters To You' : 'What this means for you'}
              </h2>
              <div className="profile-badge">{profile} profile</div>
              <ul className="footer-list">
                {(article.personalImpact[profile] || article.personalImpact.general).map((impact, i) => (
                  <li key={i}>{getLocalizedText(impact)}</li>
                ))}
              </ul>
            </section>

            {/* Action Suggestions */}
            <section className="footer-insight-card" style={{ marginBottom: 0 }}>
              <h2 className="footer-section-title">
                {profile === 'youngExplorer' ? 'Things You Can Do!' : 'Action Suggestions'}
              </h2>
              <ul className="footer-list">
                {(article.whatToDo[profile] || article.whatToDo.general).map((action, i) => (
                  <li key={i}>{getLocalizedText(action)}</li>
                ))}
              </ul>
            </section>
          </div>
        </div>
      </div>

      {/* Quiz for Young Explorer */}
      {profile === 'youngExplorer' && article.quiz && (
        <div className="quiz-box fade-in">
          <h3 className="font-heading text-lg mb-2" style={{ color: '#86198f', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BrainCircuit size={20} /> Quick Quiz!
          </h3>
          <p className="mb-3 font-medium" style={{ color: '#701a75' }}>{getLocalizedText(article.quiz.question)}</p>
          <div>
            {article.quiz.options.map((opt, i) => {
              let statusClass = '';
              if (selectedOpt !== null) {
                if (i === article.quiz.answerIndex) statusClass = 'correct';
                else if (i === selectedOpt) statusClass = 'wrong';
              }
              return (
                <button
                  key={i}
                  className={`quiz-option ${statusClass}`}
                  onClick={() => { if (selectedOpt === null) setSelectedOpt(i); }}
                  disabled={selectedOpt !== null}
                >
                  <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    {getLocalizedText(opt)}
                    {statusClass === 'correct' && <CheckCircle2 size={18} />}
                    {statusClass === 'wrong' && <XCircle size={18} />}
                  </span>
                </button>
              )
            })}
          </div>
        </div>
      )}


      {/* Confidence & Disclaimer */}
      <section className="disclaimer text-sm text-muted">
        <div className="confidence-badge">
          {lang === 'en' ? 'AI Confidence' : 'AI सटीकता'}: {getLocalizedText(article.confidence)}
        </div>
        <p className="font-modern">{getLocalizedText(article.disclaimer)}</p>
      </section>
    </div>
  );
}
