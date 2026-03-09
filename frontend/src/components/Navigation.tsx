import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();

  const tabs = [
    { name: 'Upload Data', path: '/' },
    { name: 'Portfolio', path: '/portfolio' },
    { name: 'Capital Gains', path: '/results' },
    { name: 'Trade Simulator', path: '/simulator' },
  ];

  return (
    <nav className="flex space-x-4 border-b border-gray-200">
      {tabs.map((tab) => (
        <Link
          key={tab.name}
          to={tab.path}
          className={`py-4 px-1 border-b-2 font-medium text-sm ${
            location.pathname === tab.path
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
        >
          {tab.name}
        </Link>
      ))}
    </nav>
  );
};

export default Navigation;
