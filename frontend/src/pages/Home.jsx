import { Link, useLocation } from 'react-router-dom';
import './Home.css';

function Home() {
  const location = useLocation();
  return (
    <ul className='menu-list'>
      <li>
              <Link
                to="/graph"
                className={location.pathname === '/graph' ? 'active' : ''}
              >
                GRAPH
              </Link>
      </li>
      <li>
              <Link
                to="/reputation"
                className={location.pathname === '/reputation' ? 'active' : ''}
              >
                ADD PAPER
              </Link>
      </li>
      <li>
              <Link
                to="/citations"
                className={location.pathname === '/citations' ? 'active' : ''}
              >
                CITATION GEN
              </Link>
      </li>
      <li>
              <Link
                to="/summary"
                className={location.pathname === '/summary' ? 'active' : ''}
              >
                SUMMARY
              </Link>
      </li>
      <li>
              <Link
                to="/profile"
                className={location.pathname === '/profile' ? 'active' : ''}
              >
                Profile
              </Link>
        </li>
    </ul>
  );
}

export default Home