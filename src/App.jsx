import React, { useState, useEffect, useRef } from 'react';
import { 
  User, ChevronRight, ArrowLeft, Languages, Headphones, MonitorPlay,
  ArrowUp, ArrowDown, Minus, TrendingUp, TrendingDown,
  BrainCircuit, GraduationCap, Briefcase, Globe,
  Rocket, Lightbulb, CheckCircle2, XCircle
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
    id: '1',
    category: 'Global Trends',
    title: 'Middle East Conflict Impacts Global Trade Routes',
    hindiTitle: 'मध्य पूर्व संघर्ष का वैश्विक व्यापार पर प्रभाव',
    marathiTitle: 'मध्य पूर्व संघर्षामुळे जागतिक व्यापारावर परिणाम',
    summary: 'Rising tensions disrupt major shipping lanes, affecting logistics and global supply chains.',
    hindiSummary: 'बढ़ते तनाव से प्रमुख शिपिंग मार्ग बाधित हो रहे हैं।',
    marathiSummary: 'वाढत्या तणावामुळे प्रमुख शिपिंग मार्ग विस्कळीत.',
    image: 'https://images.unsplash.com/photo-1581093458791-9f3c3900df4b?auto=format&fit=crop&w=800&q=80',
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
    id: '2',
    category: 'AI & Future',
    title: 'Generative AI Accelerates Tech Automation',
    hindiTitle: 'जेनरेटिव एआई ने टेक ऑटोमेशन को गति दी',
    marathiTitle: 'जनरेटिव्ह एआय मुळे टेक ऑटोमेशनमध्ये गती',
    summary: 'New AI models are fundamentally shifting how code and daily tasks are executed.',
    hindiSummary: 'नए एआई मॉडल कोड और दैनिक कार्यों के निष्पादन के तरीके को बदल रहे हैं।',
    marathiSummary: 'नवीन एआय मॉडेल्स काम करण्याच्या पद्धतीत बदल करत आहेत.',
    image: 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=800&q=80',
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
      youngExplorer: [{ en: 'Ask a teacher how AI can help you study!', hi: 'शिक्षक से पूछें कि एआई कैसे मदद कर सकता है!' }]
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
    id: '3',
    category: 'Science',
    title: 'New Robotic Rover Detects Subsurface Mars Ice',
    hindiTitle: 'रोवर ने मंगल पर बर्फ की खोज की',
    marathiTitle: 'रोव्हरला मंगळावर बर्फ सापडला',
    summary: 'A breakthrough discovery of pristine water ice could fuel future manned missions.',
    hindiSummary: 'स्वच्छ पानी की बर्फ की खोज भविष्य के मानव मिशन को ऊर्जा दे सकती है।',
    marathiSummary: 'पाण्याची बर्फाची शोध भविष्यातील मानवी मिशनला चालना देऊ शकते.',
    image: 'https://images.unsplash.com/photo-1614730321146-b6fa6a46bcb4?auto=format&fit=crop&w=800&q=80',
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
  }
];

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('landing'); 
  const [profile, setProfile] = useState(null);
  const [selectedArticleId, setSelectedArticleId] = useState(null);
  const [lang, setLang] = useState('en'); 

  useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash.slice(1);
      if (['landing', 'profile', 'feed', 'insight'].includes(hash)) {
        setCurrentScreen(hash);
      } else {
        window.location.hash = 'landing';
        setCurrentScreen('landing');
      }
    };
    
    if (!window.location.hash) {
      window.location.hash = 'landing';
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
        <ProfileSelection onSelect={handleProfileSelect} lang={lang} />
      )}
      {currentScreen === 'feed' && (
        <FeedScreen 
          profile={profile} 
          lang={lang}
          onProfileClick={() => navigate('profile')}
          onArticleClick={handleArticleSelect} 
        />
      )}
      {currentScreen === 'insight' && (
        <InsightScreen 
          articleId={selectedArticleId} 
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
          InsightX <span style={{color: 'var(--accent-color)'}}>AI</span>
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

function ProfileSelection({ onSelect, lang }) {
  const profiles = [
    { id: 'student', title: lang==='en'?'Student':'छात्र', desc: lang==='en'?'Focus on tech, careers & future.':'तकनीक व करियर पर जोर', icon: <GraduationCap /> },
    { id: 'investor', title: lang==='en'?'Investor / Business':'निवेशक / व्यापार', desc: lang==='en'?'Markets, economy & policy.':'बाजार व अर्थव्यवस्था', icon: <Briefcase /> },
    { id: 'general', title: lang==='en'?'General':'सामान्‍य', desc: lang==='en'?'Mixed global & national feed.':'मिश्रित समाचार फीड', icon: <Globe /> },
    { id: 'youngExplorer', title: lang==='en'?'Young Explorer':'युवा खोजकर्ता', desc: lang==='en'?'Simplified news & science facts.':'सरल विज्ञान व तथ्य', icon: <BrainCircuit /> },
  ];

  return (
    <div className="fade-in main-wrapper flex flex-col items-center justify-center p-4" style={{ minHeight: '100vh' }}>
      <h1 className="text-2xl mb-1 text-center font-bold">
        {lang === 'en' ? 'Select Profile' : 'प्रोफ़ाइल चुनें'}
      </h1>
      <p className="text-muted mb-4 text-center font-modern">
        {lang === 'en' ? 'Personalize your news intelligence feed.' : 'अपने समाचार फ़ीड को वैयक्तिकृत करें।'}
      </p>
      
      <div className="flex flex-col gap-3 w-full" style={{ maxWidth: '400px', marginTop: '2rem' }}>
        {profiles.map(p => (
          <div key={p.id} className="profile-card" onClick={() => onSelect(p.id)}>
            <div className="profile-icon-wrapper">
              {p.icon}
            </div>
            <div className="profile-content">
              <span className="profile-title">{p.title}</span>
              <span className="profile-desc">{p.desc}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function FeedScreen({ profile, lang, onProfileClick, onArticleClick }) {
  const [activeCategory, setActiveCategory] = useState('All');
  const [subTab, setSubTab] = useState('top'); // 'top' or 'forYou'
  
  const importantNews = NEWS_DATA.filter(n => n.isImportant);
  let feedNews = NEWS_DATA.filter(n => !n.isImportant);

  if (activeCategory !== 'All') {
    feedNews = NEWS_DATA.filter(n => n.category === activeCategory);
  }

  // Pre-defined categories
  const categories = ['All', 'Tech Innovation', 'AI & Future', 'Startups', 'Science', 'Global Trends', 'Sports', 'Entertainment', 'Lifestyle', 'Education', 'Economy', 'Careers', 'Politics'];

  return (
    <div className="fade-in bg-white" style={{ minHeight: '100vh' }}>
      <header className="header">
        <div>
          <div className="logo-text">InsightX <span>AI</span></div>
          <div className="tagline">
            {profile === 'youngExplorer' ? (lang==='en'?'Learn the World!':'दुनिया सीखें!') : (lang==='en'?'Understand the World Around You':'दुनिया को समझें')}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button className="profile-icon" onClick={onProfileClick} aria-label="Change Profile">
            <User size={20} />
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
            {NEWS_DATA.map(news => (
              <div key={`quick-${news.id}`} className="quick-read-item" onClick={() => onArticleClick(news.id)}>
                <span className="quick-tag">{news.category}</span>
                <h4 className="quick-headline">{lang === 'en' ? news.title : news.hindiTitle}</h4>
              </div>
            ))}
          </div>
        </aside>

        {/* 2️⃣ CENTER MAIN FEED */}
        <main className="center-feed p-4">
          {/* Categories */}
          {(profile === 'student' || profile === 'general') && (
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
          )}

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
        </main>

        {/* 3️⃣ RIGHT SIDEBAR: Visual Stories */}
        <aside className="sidebar right-sidebar">
          <div className="sidebar-header">
            <MonitorPlay size={16} />
            <h2 className="sidebar-title">Visual Stories</h2>
          </div>
          <div className="sidebar-scroll no-scrollbar">
            {NEWS_DATA.map(news => (
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

function InsightScreen({ articleId, profile, lang, setLang, onBack }) {
  const article = NEWS_DATA.find(n => n.id === articleId) || NEWS_DATA[0];
  const [isPlaying, setIsPlaying] = React.useState(false);
  const [showVideo, setShowVideo] = React.useState(false);
  const [selectedOpt, setSelectedOpt] = React.useState(null);
  const audioRef = React.useRef(null);

  const getLocalizedText = (obj) => {
    return lang === 'en' ? obj.en : (lang === 'hi' ? obj.hi : obj.marathi); // simplified handling
  };

  const getPropText = (obj, enKey, hiKey, mrKey) => {
    return lang === 'en' ? obj[enKey] : (lang === 'hi' ? obj[hiKey] : (obj[mrKey] || obj[hiKey]));
  };

  const renderDirectionIcon = (direction) => {
    switch(direction) {
      case 'up': return <ArrowUp size={24} className="text-accent" style={{color: 'var(--accent-color)'}} />;
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
    <div className="fade-in bg-white" style={{ minHeight: '100vh', paddingBottom: '2rem' }}>
      <header className="insight-header main-wrapper">
        <button className="back-btn" onClick={onBack} aria-label="Go Back" style={{width: 'fit-content'}}>
          <ArrowLeft size={24} />
        </button>
        <div style={{ marginTop: '0.5rem' }}>
          <h1 className="insight-title">{getPropText(article, 'title', 'hindiTitle', 'marathiTitle')}</h1>
          <p className="text-muted mt-2 font-modern" style={{fontSize: '1.1rem'}}>
            {getPropText(article, 'summary', 'hindiSummary', 'marathiSummary')}
          </p>
        </div>
      </header>

      {/* Multimodal Actions */}
      <div className="multimodal-bar main-wrapper">
        <button className="action-btn" onClick={cycleLanguage}>
          <Languages size={18} />
          {lang === 'en' ? 'Translate to Hindi' : 'English में पढ़ें'}
        </button>
        <button className="action-btn" onClick={toggleAudio}>
          <Headphones size={18} />
          {isPlaying ? (lang === 'en' ? 'Pause Audio' : 'ऑडियो रोकें') : (lang === 'en' ? 'Listen' : 'सुनें')}
        </button>
        {article.videoSrc && (
          <button className="action-btn" onClick={() => setShowVideo(!showVideo)}>
            <MonitorPlay size={18} />
            {lang === 'en' ? 'Watch AI Video' : 'वीडियो देखें'}
          </button>
        )}
      </div>

      {/* Speech synthesized automatically, no <audio> tag needed for demo */}

      <div className="main-wrapper">
        {showVideo && article.videoSrc && (
          <div className="insight-section" style={{ background: '#0f172a', display: 'flex', justifyContent: 'center', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
            <p style={{ color: 'white', fontSize: '0.8rem', opacity: 0.8 }} className="font-modern">
              AI Generated Summary
            </p>
            <video style={{ width: '100%', maxWidth: '600px', borderRadius: '12px' }} controls autoPlay loop>
              <source src={article.videoSrc} type="video/mp4" />
            </video>
          </div>
        )}

        {article.image && !showVideo && (
          <div style={{ width: '100%', height: 'auto', background: '#f5f5f5', borderBottom: '1px solid var(--border-color)' }}>
            <img src={article.image} alt="News context" style={{ width: '100%', height: '280px', objectFit: 'cover', display: 'block' }} />
          </div>
        )}

        {/* Young Explorer Special Features */}
        {profile === 'youngExplorer' && article.didYouKnow && (
          <div className="did-you-know fade-in">
            <Lightbulb size={40} color="#ca8a04" style={{flexShrink: 0}} />
            <div>
              <h3 className="font-heading text-lg" style={{color: '#854d0e', marginBottom: '0.25rem'}}>Did You Know?</h3>
              <p style={{color: '#713f12'}}>{getLocalizedText(article.didYouKnow)}</p>
            </div>
          </div>
        )}

        {/* Impact Chain */}
        <section className="insight-section">
          <h2 className="section-title">
            {profile === 'youngExplorer' ? (lang==='en'?'How Does This Work?':'यह कैसे काम करता है?') : (lang==='en'?'Chain Reaction':'प्रतिक्रिया श्रृंखला')}
          </h2>
          <div className="impact-chain">
            {article.impactChain.map((node, i) => (
              <div key={i} className="impact-node">
                <div className={`node-dot ${node.direction}`}>
                  {renderDirectionIcon(node.direction)}
                </div>
                <div className="node-text">
                  {lang === 'en' ? node.text : (node.hindiText || node.text)}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Personal Impact */}
        <section className="insight-section">
          <h2 className="section-title" style={{marginBottom: '0.5rem'}}>
            {profile === 'youngExplorer' ? (lang==='en'?'Why It Matters To You':'आपके लिए यह क्यों मायने रखता है') : (lang==='en'?'What this means for you':'आपके लिए इसका क्या अर्थ है')}
          </h2>
          <p className="text-sm text-muted mb-3 uppercase tracking-wide font-bold" style={{color: 'var(--accent-color)'}}>
            ({lang==='en'?profile+' profile':profile+' प्रोफ़ाइल'})
          </p>
          <ul className="custom-list">
            {(article.personalImpact[profile] || article.personalImpact.general).map((impact, i) => (
              <li key={i}>{getLocalizedText(impact)}</li>
            ))}
          </ul>
        </section>

        {/* Action Suggestions */}
        <section className="insight-section" style={{ background: 'var(--bg-color)' }}>
          <h2 className="section-title">
            {profile === 'youngExplorer' ? (lang==='en'?'Things You Can Do!':'आप क्या कर सकते हैं!') : (lang==='en'?'Action Suggestions':'आगे क्या करें')}
          </h2>
          <ul className="custom-list">
            {(article.whatToDo[profile] || article.whatToDo.general).map((action, i) => (
              <li key={i}>{getLocalizedText(action)}</li>
            ))}
          </ul>
        </section>

        {/* Quiz for Young Explorer */}
        {profile === 'youngExplorer' && article.quiz && (
          <div className="quiz-box fade-in">
            <h3 className="font-heading text-lg mb-2" style={{color: '#86198f', display: 'flex', alignItems: 'center', gap: '8px'}}>
              <BrainCircuit size={20} /> Quick Quiz!
            </h3>
            <p className="mb-3 font-medium" style={{color: '#701a75'}}>{getLocalizedText(article.quiz.question)}</p>
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
                    onClick={() => { if(selectedOpt === null) setSelectedOpt(i); }}
                    disabled={selectedOpt !== null}
                  >
                    <span style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
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

        {/* What to watch next (hidden for young explorer to simplify) */}
        {profile !== 'youngExplorer' && (
          <section className="insight-section border-b-0">
            <h2 className="section-title">
              {lang === 'en' ? 'What to watch next' : 'आगे क्या देखना है'}
            </h2>
            <div className="flex flex-col gap-2">
              {article.watchNext.map((watch, i) => (
                <div key={i} className="flex items-center gap-2 text-sm p-3 border rounded shadow-sm bg-white" style={{borderColor: 'var(--border-color)', borderRadius: 'var(--radius-sm)'}}>
                  <ChevronRight size={16} color="var(--accent-color)" />
                  <span className="font-medium">{getLocalizedText(watch)}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Confidence & Disclaimer */}
        <section className="disclaimer text-sm text-muted">
          <div className="confidence-badge">
            {lang === 'en' ? 'AI Confidence' : 'AI सटीकता'}: {getLocalizedText(article.confidence)}
          </div>
          <p className="font-modern">{getLocalizedText(article.disclaimer)}</p>
        </section>
      </div>
    </div>
  );
}
