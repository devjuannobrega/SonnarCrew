import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { 
  Code2, 
  Zap, 
  Shield, 
  BarChart3, 
  History, 
  ChevronRight,
  GitBranch,
  Terminal
} from "lucide-react";

const Index = () => {
  const navigate = useNavigate();
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  const features = [
    {
      icon: <Code2 className="h-6 w-6" />,
      title: "Code Analysis",
      description: "Advanced Python code analysis with AI-powered suggestions"
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Security Check",
      description: "Comprehensive security vulnerability detection"
    },
    {
      icon: <BarChart3 className="h-6 w-6" />,
      title: "Performance Metrics",
      description: "Detailed performance analysis and optimization tips"
    },
    {
      icon: <History className="h-6 w-6" />,
      title: "Analysis History",
      description: "Track all your code reviews and improvements"
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-transparent to-accent/20" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center space-y-8">
            {/* Logo/Brand */}
            <div className={`flex items-center justify-center space-x-3 mb-8 transition-all duration-700 ${isLoaded ? 'animate-fade-in-up' : 'opacity-0 translate-y-10'}`}>
              <div className="tech-gradient p-3 rounded-xl tech-glow animate-float">
                <Terminal className="h-8 w-8 text-primary-foreground" />
              </div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Python Review
              </h1>
            </div>

            {/* Main Heading */}
            <div className="space-y-4">
              <div className={`transition-all duration-1000 delay-200 ${isLoaded ? 'animate-scale-in' : 'opacity-0 scale-95'}`}>
                <Badge variant="secondary" className="px-4 py-2 tech-glow animate-pulse-glow">
                  <Zap className="h-4 w-4 mr-2" />
                  AI-Powered Code Analysis
                </Badge>
              </div>
              
              <div className={`transition-all duration-1000 delay-400 ${isLoaded ? 'animate-fade-in' : 'opacity-0'}`}>
                <h2 className="text-5xl md:text-6xl font-bold leading-tight">
                  Elevate Your
                  <span className="block tech-gradient bg-clip-text text-transparent animate-pulse-glow">
                    Python Code
                  </span>
                </h2>
              </div>
              
              <div className={`transition-all duration-1000 delay-600 ${isLoaded ? 'animate-fade-in-up' : 'opacity-0 translate-y-10'}`}>
                <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                  Get instant AI-powered code reviews, security analysis, and performance optimization 
                  suggestions for your Python projects.
                </p>
              </div>
            </div>

            {/* CTA Button */}
            <div className={`pt-8 transition-all duration-1000 delay-800 ${isLoaded ? 'animate-slide-in-right' : 'opacity-0 translate-x-full'}`}>
              <Button
                size="lg"
                className="tech-gradient px-8 py-6 text-lg font-semibold tech-glow hover:scale-110 transition-all duration-300 animate-pulse-glow"
                onClick={() => navigate('/chat')}
              >
                Start Code Review
                <ChevronRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className={`text-center mb-16 transition-all duration-1000 ${isLoaded ? 'animate-fade-in-up' : 'opacity-0 translate-y-10'}`}>
          <h3 className="text-3xl font-bold mb-4">Powerful Analysis Features</h3>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Comprehensive code analysis powered by advanced AI agents
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Card 
              key={index} 
              className={`tech-card p-6 group cursor-pointer hover:scale-105 transition-all duration-500 ${
                isLoaded ? 'animate-fade-in-up' : 'opacity-0 translate-y-10'
              }`}
              style={{ animationDelay: `${1000 + index * 200}ms` }}
            >
              <div className="text-primary mb-4 group-hover:text-accent transition-colors duration-300 group-hover:scale-110">
                {feature.icon}
              </div>
              <h4 className="text-lg font-semibold mb-2">{feature.title}</h4>
              <p className="text-muted-foreground text-sm">{feature.description}</p>
            </Card>
          ))}
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-card/50 backdrop-blur-sm border-y border-border/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div className={`space-y-2 transition-all duration-1000 ${isLoaded ? 'animate-scale-in' : 'opacity-0 scale-95'}`} style={{ animationDelay: '1500ms' }}>
              <div className="text-3xl font-bold text-primary animate-pulse-glow">99.9%</div>
              <div className="text-muted-foreground">Accuracy Rate</div>
            </div>
            <div className={`space-y-2 transition-all duration-1000 ${isLoaded ? 'animate-scale-in' : 'opacity-0 scale-95'}`} style={{ animationDelay: '1700ms' }}>
              <div className="text-3xl font-bold text-accent animate-pulse-glow">&lt; 2s</div>
              <div className="text-muted-foreground">Average Analysis Time</div>
            </div>
            <div className={`space-y-2 transition-all duration-1000 ${isLoaded ? 'animate-scale-in' : 'opacity-0 scale-95'}`} style={{ animationDelay: '1900ms' }}>
              <div className="text-3xl font-bold text-primary animate-pulse-glow">3+</div>
              <div className="text-muted-foreground">AI Agents Working</div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <Card className={`tech-card p-12 text-center transition-all duration-1000 hover:scale-105 ${isLoaded ? 'animate-fade-in' : 'opacity-0'}`} style={{ animationDelay: '2100ms' }}>
          <div className="space-y-6">
            <div className="mx-auto w-16 h-16 tech-gradient rounded-full flex items-center justify-center tech-glow animate-float">
              <GitBranch className="h-8 w-8 text-primary-foreground" />
            </div>
            
            <div>
              <h3 className="text-2xl font-bold mb-4">Ready to Improve Your Code?</h3>
              <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
                Join thousands of developers who trust our AI-powered code analysis 
                to write better, more secure Python code.
              </p>
              
              <Button
                size="lg"
                className="tech-gradient px-8 py-4 tech-glow hover:scale-110 transition-all duration-300 animate-pulse-glow group"
                onClick={() => navigate('/chat')}
              >
                Launch Python Review
                <Terminal className="ml-2 h-5 w-5 transition-transform group-hover:rotate-12" />
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Index;