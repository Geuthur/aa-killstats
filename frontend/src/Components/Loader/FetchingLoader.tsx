// Styles
import styles from '@/Components/Loader/FetchingLoader.module.css';

interface LoaderProps {
  message?: string;
  className?: string;
}

export const FetchingLoader = ({ message, className = '' }: LoaderProps = {}) => {
  return (
    <div className={`${styles['flex-container-loader']} ${className}`}>
      <div
        className="spinner-border text-info"
        role="status"
        style={{ width: '2.5rem', height: '2.5rem' }}
      >
        <span className="visually-hidden">Loading...</span>
      </div>
      {message && (
        <span className="text-zinc-400 text-sm font-medium mt-3 tracking-wide">
          {message}
        </span>
      )}
    </div>
  );
};

export default FetchingLoader;
