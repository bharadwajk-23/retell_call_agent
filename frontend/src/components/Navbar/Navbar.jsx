import { useEffect, useRef } from 'react'
import styles from './Navbar.module.css'

export function Navbar({ searchTerm, onSearchChange, onReset, resetting }) {
  const searchRef = useRef(null)

  useEffect(() => {
    function handleShortcut(event) {
      const isShortcut = (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k'
      if (isShortcut) {
        event.preventDefault()
        searchRef.current?.focus()
      }
    }
    window.addEventListener('keydown', handleShortcut)
    return () => window.removeEventListener('keydown', handleShortcut)
  }, [])

  return (
    <header className={styles.navbar}>
      <div className={styles.brand}>
        <span className={styles.logo} aria-hidden="true">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2a1 1 0 0 1 1.02-.24c1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1.02l-2.2 2.2Z"
              fill="#ffffff"
            />
          </svg>
        </span>
        <div>
          <p className={styles.brandName}>MediCare</p>
          <p className={styles.brandSubtitle}>AI Call Assistant</p>
        </div>
      </div>

      <div className={styles.searchWrap}>
        <span className={styles.searchIcon} aria-hidden="true">
          🔍
        </span>
        <input
          ref={searchRef}
          type="text"
          className={styles.searchInput}
          placeholder="Search patients, calls…"
          value={searchTerm}
          onChange={(event) => onSearchChange(event.target.value)}
        />
        <kbd className={styles.searchHint}>⌘K</kbd>
      </div>

      <div className={styles.actions}>
        <button
          type="button"
          className={styles.resetButton}
          onClick={onReset}
          disabled={resetting}
          title="Reset demo data"
        >
          {resetting ? 'Resetting…' : 'Reset'}
        </button>
      </div>
    </header>
  )
}
