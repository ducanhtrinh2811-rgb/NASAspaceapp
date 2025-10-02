import { useLocation } from "react-router-dom";

export function Footer() {
  const location = useLocation();
  const isHomePage = location.pathname === '/' || location.pathname === '/home';


  if (isHomePage) {
    // Detailed footer for home page
    return (
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <h3 className="text-xl font-bold mb-4">NEROMIND</h3>
              <p className="text-gray-300 mb-4">
There is a three-star making a straight line in the night sky 
It's been seen through The Eyes of A child
Darkness doesn't mean loneliness 
It's about Contemplation
              </p>
              <p className="text-blue-400 font-semibold">SHARE TO BE SHARED</p>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-300">
                <li><a href="#topics" className="hover:text-blue-400 transition-colors">Topics</a></li>
                <li><a href="#about" className="hover:text-blue-400 transition-colors">About</a></li>
                <li><a href="#feedback" className="hover:text-blue-400 transition-colors">Feedback</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold mb-4">Research Areas</h4>
              <ul className="space-y-2 text-gray-300">
                <li>Vertebrate Studies</li>
                <li>Plant Biology</li>
                <li>Microbiology</li>
                <li>Fungal Research</li>
                <li>Human Cell Biology</li>
                <li>Systems Biology</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 NEROMIND - NASA Space Apps Challenge 2025. All rights reserved.</p>
          </div>
        </div>
      </footer>
    );
  }

  // Simplified footer for other pages
  return (
    <footer 
      className="bg-gray-900 text-white py-8 relative overflow-hidden"
      style={{
        background: 'linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%)',
        position: 'relative'
      }}
    >
      {/* Star field background */}
      <div 
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage: `
            radial-gradient(2px 2px at 20px 30px, #eee, transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.8), transparent),
            radial-gradient(1px 1px at 90px 40px, #fff, transparent),
            radial-gradient(1px 1px at 130px 80px, rgba(255,255,255,0.6), transparent),
            radial-gradient(2px 2px at 160px 30px, #ddd, transparent)
          `,
          backgroundRepeat: 'repeat',
          backgroundSize: '200px 100px'
        }}
      />
      
      <div className="container mx-auto px-6 relative z-10">
        <div className="flex items-center justify-between">
          {/* Left: Three logos */}
          <div className="flex items-center space-x-6">
            <a 
              href="https://www.facebook.com/share/1EymDZTzCc/?mibextid=wwXIfr" 
              target="_blank" 
              rel="noopener noreferrer"
              className="transition-transform duration-300 hover:scale-110"
            >
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center font-bold text-white">
                N
              </div>
            </a>
            
            <a 
              href="https://www.facebook.com/profile.php?id=61576561960061" 
              target="_blank" 
              rel="noopener noreferrer"
              className="transition-transform duration-300 hover:scale-110"
            >
              <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center font-bold text-white">
                M
              </div>
            </a>
            
            <a 
              href="https://www.facebook.com/SVNCKH" 
              target="_blank" 
              rel="noopener noreferrer"
              className="transition-transform duration-300 hover:scale-110"
            >
              <div className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center font-bold text-white">
                S
              </div>
            </a>
          </div>
          
          {/* Center: SHARE TO BE SHARED */}
          <div className="text-center">
            <p className="text-blue-400 font-semibold text-lg tracking-wide">
              SHARE TO BE SHARED
            </p>
          </div>
          
          {/* Right: Empty space for balance */}
          <div className="w-48"></div>
        </div>
      </div>
    </footer>
  );
}