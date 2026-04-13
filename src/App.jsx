
import React, { useState, useEffect, useRef } from 'react';
import { 
  User, ChevronRight, ArrowLeft, Languages, Headphones, MonitorPlay,
  ArrowUp, ArrowDown, Minus, TrendingUp, TrendingDown,
  BrainCircuit, GraduationCap, Briefcase, Globe,
  Rocket, Lightbulb, CheckCircle2, XCircle, LogOut,
  MapPin, CloudSun, Calendar
} from 'lucide-react';
import './App.css';



export default function App() {
  const [currentScreen, setCurrentScreen] = useState('landing'); 
  const [profile, setProfile] = useState(null);
  const [selectedArticleId, setSelectedArticleId] = useState(null);
  const [lang, setLang] = useState('en'); 
  const [articles, setArticles] = useState([]);

  const fetchFeed = (cat = 'All') => {
    fetch(`http://localhost:8001/api/feed?category=${encodeURIComponent(cat)}`)
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success' && data.articles && data.articles.length > 0) {
          const mappedArticles = data.articles.map((a, idx) => ({
             id: a.id,
             category: a.category || 'Global Trends',
             title: a.title,
             hindiTitle: a.title,
             marathiTitle: a.title,
             summary: a.source || '',
             hindiSummary: a.source || '',
             marathiSummary: a.source || '',
             image: a.image_url || a.img_url || a.thumbnail || '',
             url: a.url,
             content: a.content || '',
             isImportant: idx < 2
          }));
          if (cat === 'All') {
            setArticles(mappedArticles);
          } else {
            setArticles(prev => {
              const others = prev.filter(p => p.category !== cat && !p.id.toString().startsWith('gnews_'));
              return [...mappedArticles, ...others];
            });
          }
        }
      })
      .catch(err => console.error("Error fetching feed:", err));
  };

  useEffect(() => {
    // Fetch initial feed
    fetchFeed('All');

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
    // Persist the change
    const savedUser = JSON.parse(localStorage.getItem('insightx_user') || '{}');
    savedUser.role = selectedProfile;
    localStorage.setItem('insightx_user', JSON.stringify(savedUser));
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
          fetchFeed={fetchFeed}
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

function OnboardingScreen({ onComplete, lang }) {
  const [formData, setFormData] = useState(() => {
    const savedUser = JSON.parse(localStorage.getItem('insightx_user') || '{}');
    return {
      name: savedUser.name || '',
      email: savedUser.email || '',
      role: savedUser.role || 'student',
      interests: savedUser.interests || []
    };
  });
  const [interestInput, setInterestInput] = useState('');

  const suggestedInterests = ['AI', 'Technology', 'Finance', 'Space', 'Startups', 'Sports', 'Economy'];

  const profiles = [
    { id: 'student', title: lang==='en'?'Student':'छात्र', icon: <GraduationCap size={20} /> },
    { id: 'investor', title: lang==='en'?'Investor':'निवेशक', icon: <Briefcase size={20} /> },
    { id: 'general', title: lang==='en'?'General':'सामान्‍य', icon: <Globe size={20} /> },
    { id: 'youngExplorer', title: lang==='en'?'Young Explorer':'युवा खोजकर्ता', icon: <BrainCircuit size={20} /> },
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
        
        if (response.ok) {
            const data = await response.json();
            if (data.user && data.user.id) {
                updatedUser.id = data.user.id;
            }
        } else {
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
                onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>{lang === 'en' ? 'Email' : 'ईमेल'}</label>
              <input 
                type="email" 
                placeholder={lang === 'en' ? 'Enter your email' : 'अपना ईमेल दर्ज करें'} 
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
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
                onClick={() => setFormData({...formData, role: p.id})}
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


function FeedScreen({ articles, profile, lang, onProfileClick, onArticleClick, fetchFeed }) {
  const [activeCategory, setActiveCategory] = useState('All');
  const [subTab, setSubTab] = useState('top'); // 'top' or 'forYou'
  
  const importantNews = articles.filter(n => n.isImportant);
  let feedNews = articles.filter(n => !n.isImportant);

  if (activeCategory !== 'All') {
    feedNews = articles.filter(n => n.category === activeCategory);
  }

  // Define forYouNews logic
  const userData = JSON.parse(localStorage.getItem('insightx_user') || '{}');
  const userInterests = userData.interests || [];
  
  const forYouNews = articles.filter(news => {
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
            <span>Pune, IN</span>
          </div>
          <div className="context-item divider">|</div>
          <div className="context-item">
            <Calendar size={14} />
            <span>{new Date().toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })}</span>
          </div>
          <div className="context-item divider">|</div>
          <div className="context-item">
            <CloudSun size={14} />
            <span>30°C</span>
          </div>
        </div>

        <div className="header-center">
          <div className="logo-text" onClick={() => window.location.hash = 'landing'} style={{ cursor: 'pointer' }}>
            InsightX <span>AI</span>
          </div>
          <div className="tagline">
            {profile === 'youngExplorer' ? (lang==='en'?'Learn the World!':'दुनिया सीखें!') : (lang==='en'?'Understand the World Around You':'दुनिया को समझें')}
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
                    if (fetchFeed) fetchFeed(cat);
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
    const userData = JSON.parse(localStorage.getItem('insightx_user') || '{}');
    fetch('http://localhost:8001/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
         article_id: articleId && !String(articleId).startsWith('gnews_') ? articleId : null, 
         url: article?.url || null,
         title: article?.title || null,
         content: article?.content || null,
         profile: profile || 'student', 
         user_id: userData.id 
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data && data.profile_used) {
        // Map backend InsightOutput to frontend expected structure
        const nextStepsMapped = data.next_steps ? data.next_steps.map(step => ({ en: step, hi: step })) : [];
        let personalImpacts = [];
        if (data.profile_specific_insights) {
          Object.values(data.profile_specific_insights).filter(Boolean).forEach(val => {
            if (Array.isArray(val)) {
              val.forEach(item => personalImpacts.push({ en: item, hi: item }));
            } else {
              personalImpacts.push({ en: String(val), hi: String(val) });
            }
          });
        }
        
        const mapped = {
          ...baseArticle,
          summary: data.summary || baseArticle.summary,
          hindiSummary: data.summary || baseArticle.hindiSummary,
          confidence: { en: data.fact_check_confidence, hi: data.fact_check_confidence },
          didYouKnow: { en: data.simplified_explainer || '', hi: data.simplified_explainer || '' },
          impactChain: Array.isArray(data.cause_effect) ? data.cause_effect : (data.cause_effect && typeof data.cause_effect === 'object' ? Object.keys(data.cause_effect).map(k => ({ text: k, description: data.cause_effect[k], direction: 'up' })) : [{ text: data.sentiment_label, direction: data.sentiment_label === 'positive' ? 'up' : 'down' }]),
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
                   <p className="drop-cap">{getPropText(article, 'summary', 'hindiSummary', 'marathiSummary')}. {lang==='en'?'This development marks a significant shift in the current landscape, bringing forth new opportunities and challenges for stakeholders. Experts suggest that we are entering a pivotal moment where technological and social forces converge.':'यह विकास वर्तमान परिदृश्य में एक महत्वपूर्ण बदलाव का संकेत देता है, जो हितधारकों के लिए नए अवसर और चुनौतियां लेकर आता है।'}</p>
                   
                   <p>{lang==='en'?'The underlying data reveals a steady progression towards broader infrastructure support and global integration. As markets react to these shifting dynamics, the impact is being felt across multiple sectors, reinforcing the need for adaptive strategies and intelligent forecasting.':'अंतर्निहित डेटा व्यापक बुनियादी ढांचे के समर्थन और वैश्विक एकीकरण की ओर निरंतर प्रगति को प्रकट करता है।'}</p>
                </div>
              ) : (
                <div className="full-view fade-in">
                   <div className="inline-image image-left">
                     <img src="https://images.unsplash.com/photo-1544006659-f0b21f04cb1b?auto=format&fit=crop&w=400&q=80" alt="Innovation" />
                     <span className="caption">Expert Analysis</span>
                   </div>
                   <p className="drop-cap">{lang==='en'?'In an era defined by rapid transformation, the recent developments in our local and global systems present a compelling narrative of innovation and resilience. This extensive report underscores how fundamental shifts in resources and technology are reshaping established norms across the globe. As we delve deeper into the core drivers of this change, it becomes evident that the intersection of digital infrastructure and human ingenuity is at the forefront of the next economic cycle.':'तेजी से बदलाव के युग में, हमारी स्थानीय और वैश्विक प्रणालियों में हालिया घटनाक्रम नवाचार और लचीलेपन की एक सम्मोहक कहानी पेश करते हैं।'}</p>
                   
                   <p>{lang==='en'?'Detailed analysis from top-tier research institutions highlights the critical role of systematic integration. By aligning strategic goals with technological capabilities, organizations are finding new ways to drive growth while maintaining operational stability in uncertain times. The data suggests that companies adopting a "technology-first" mindset are outperforming their peers by a significant margin. This performance gap is expected to widen as AI-driven automation becomes the standard rather than the exception.':'शीर्ष शोध संस्थानों का विस्तृत विश्लेषण व्यवस्थित एकीकरण की महत्वपूर्ण भूमिका को उजागर करता है।'}</p>
                   
                   <p>{lang==='en'?'Furthermore, the social implications of these changes are becoming increasingly apparent. From educational transformations to shifting economic models, the ripple effects are pervasive, touching every aspect of modern life. Educational institutions are already beginning to pivot their curricula toward the skills of the future, focusing on high-level cognitive tasks that complement machine efficiency. This shift represents a fundamental rebranding of the workforce as we know it, with a premium placed on adaptability and lifelong learning.':'इसके अलावा, इन परिवर्तनों के सामाजिक प्रभाव तेजी से स्पष्ट होते जा रहे हैं।'}</p>

                   <p>{lang==='en'?'Looking ahead, the long-term sustainability of these advancements will depend heavily on regulatory frameworks and ethical considerations. Policymakers are now tasked with the difficult challenge of fostering innovation while protecting public interests. Early indicators suggest a trend toward more unified global standards, which could significantly reduce friction in international trade and data exchange. As new data emerge daily, the ability to interpret and act on this information will be the primary differentiator for leaders in the coming decade.':'आगे बढ़ते हुए, इन प्रगतियों की दीर्घकालिक स्थिरता नियामक ढांचे और नैतिक विचारों पर निर्भर करेगी।'}</p>

                   <p>{lang==='en'?'In conclusion, while the path forward presents its share of complexities, the opportunities for positive impact have never been greater. By embracing these shifts with a focus on collaborative problem-solving and ethical implementation, we can ensure that the benefits of this transformation are shared broadly across society. The key takeaway for stakeholders is clear: remain agile, stay informed, and prioritize inclusive growth in every strategic decision.':'अंत में, जबकि आगे का रास्ता अपनी जटिलताओं का हिस्सा प्रस्तुत करता है, सकारात्मक प्रभाव के अवसर कभी इतने महान नहीं रहे हैं।'}</p>
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
                      <div className="chain-desc">{lang === 'en' ? (node.description || 'Direct influence on market metrics') : (node.hindiDescription || node.description || 'बाजार मेट्रिक्स पर सीधा प्रभाव')}</div>
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
                    {(article.watchNext || []).map((watch, i) => (
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


        {/* Confidence & Disclaimer */}
        <section className="disclaimer text-sm text-muted">
          <div className="confidence-badge">
            {lang === 'en' ? 'AI Confidence' : 'AI सटीकता'}: {article.confidence && getLocalizedText(article.confidence)}
          </div>
          <p className="font-modern">{article.disclaimer ? getLocalizedText(article.disclaimer) : (lang === 'en' ? 'Disclaimer: Content generated by AI.' : 'अस्वीकरण: AI द्वारा जनरेट की गई सामग्री।')}</p>
        </section>
      </div>
  );
}