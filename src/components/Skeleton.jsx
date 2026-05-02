export default function Skeleton({ rows = 4 }) {
  return (
    <div className="skeleton-stack" aria-label="Loading">
      {Array.from({ length: rows }).map((_, index) => (
        <div className="skeleton" key={index} style={{ width: `${96 - index * 8}%` }} />
      ))}
    </div>
  );
}
