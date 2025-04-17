// scenes/dashboard/components/utils/useCsvObserver.js

import { useEffect } from "react";

export default function useCsvObserver(refs, data, setActiveTab, onTabChange) {
  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
          setActiveTab(i);
          if (onTabChange) onTabChange(i);
        }
      });
    }, { threshold: 0.6 });

    refs.current.forEach((ref) => ref && observer.observe(ref));
    return () => refs.current.forEach((ref) => ref && observer.unobserve(ref));
  }, [data]);
}