import Header from '@/components/Header';
import Hero from '@/components/Hero';
import Features from '@/components/Features';
import Technology from '@/components/Technology';
import Roadmap from '@/components/Roadmap';
import Community from '@/components/Community';
import Footer from '@/components/Footer';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-black">
      <Header />
      <main>
        <Hero />
        <Features />
        <Technology />
        <Roadmap />
        <Community />
      </main>
      <Footer />
    </div>
  );
}