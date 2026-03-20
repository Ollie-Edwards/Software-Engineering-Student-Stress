export default function LinkElement({ url }) {
  if (!url) return null;

  return (
    <button
      type="button"
      onClick={(e) => {
        e.stopPropagation();
        window.open(url, "_blank");
      }}
      className="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-50 transition-colors rounded-lg"
    >
      <svg
        className="h-5 w-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
        />
      </svg>
    </button>
  );
}
