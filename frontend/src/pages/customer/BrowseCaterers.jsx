
import { useEffect, useState } from "react";
import { getCaterers, getCatererById } from "../../api";
import CatererCard from "../../components/CatererCard";

function BrowseCaterers() {
  const [caterers, setCaterers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [priceError, setPriceError] = useState("");

  const [selectedIds, setSelectedIds] = useState([]);
  const [comparisonData, setComparisonData] = useState([]);
  const [comparisonLoading, setComparisonLoading] = useState(false);
  const [comparisonError, setComparisonError] = useState("");

  // Load caterers immediately and refresh every 15 seconds
  useEffect(() => {
    let isActive = true;
    let hasLoadedOnce = false;

    async function loadCaterers() {
      try {
        const response = await getCaterers({ min_price: minPrice, max_price: maxPrice });

        if (isActive) {
          setCaterers(response.data || []);
          setError("");
        }
      } catch (err) {
        if (isActive && !hasLoadedOnce) {
          setError(err.message || "Unable to load caterers.");
        }
      } finally {
        if (isActive) {
          setLoading(false);
          hasLoadedOnce = true;
        }
      }
    }

    loadCaterers();

    const intervalId = setInterval(loadCaterers, 15000);

    return () => {
      isActive = false;
      clearInterval(intervalId);
    };
  }, [minPrice, maxPrice]);

  // Search caterers
  const filteredCaterers = caterers.filter((caterer) => {
    const search = searchTerm.trim().toLowerCase();

    const fields = [
      caterer.business_name,
      caterer.company_name,
      caterer.category,
      caterer.location,
    ];

    return (
      !search ||
      fields.some((field) =>
        String(field || "").toLowerCase().includes(search)
      )
    );
  });

  // Select or remove caterers for comparison
  function toggleComparison(caterer) {
    setComparisonError("");
    setComparisonData([]);

    if (selectedIds.includes(caterer.id)) {
      setSelectedIds(
        selectedIds.filter((id) => id !== caterer.id)
      );
      return;
    }

    if (selectedIds.length >= 3) {
      setComparisonError(
        "You can compare a maximum of 3 caterers."
      );
      return;
    }

    const firstSelected = caterers.find(
      (item) => item.id === selectedIds[0]
    );

    if (
      firstSelected?.category &&
      caterer.category &&
      firstSelected.category.toLowerCase() !==
        caterer.category.toLowerCase()
    ) {
      setComparisonError(
        "Please select caterers from the same category."
      );
      return;
    }

    setSelectedIds([...selectedIds, caterer.id]);
  }

  // Compare selected caterers
  async function compareCaterers() {
    if (selectedIds.length < 2) {
      setComparisonError(
        "Select at least two caterers to compare."
      );
      return;
    }

    setComparisonLoading(true);
    setComparisonError("");
    setComparisonData([]);

    try {
      const results = await Promise.all(
        selectedIds.map((id) => getCatererById(id))
      );

      setComparisonData(
        results.map((result) => result.data)
      );
    } catch (err) {
      setComparisonError(
        err.message ||
          "Unable to compare caterers. Please try again."
      );
    } finally {
      setComparisonLoading(false);
    }
  }

  // Clear comparison
  function clearComparison() {
    setSelectedIds([]);
    setComparisonData([]);
    setComparisonError("");
  }

  return (
    <main className="listing-page">
      <section className="listing-hero">
        <span className="eyebrow">
          SOKOCATER MARKETPLACE
        </span>

        <h1>Find Your Perfect Caterer</h1>

        <p>
          Explore catering businesses and discover packages
          for your next event.
        </p>
      </section>

      <section className="listing-content">
        <div className="listing-heading">
          <div>
            <span className="eyebrow">OUR CATERERS</span>
            <h2>Available Catering Services</h2>
          </div>
        </div>

        {/* Search */}
        <div className="caterer-search">
          <input
            type="search"
            value={searchTerm}
            onChange={(event) =>
              setSearchTerm(event.target.value)
            }
            placeholder="Search by caterer, company, category or location..."
            aria-label="Search caterers"
          />
        </div>

        {/* Price Filter */}
        <div className="caterer-search" style={{ display: "flex", gap: "10px", flexWrap: "wrap", marginTop: "10px" }}>
          <input type="number" min="0" placeholder="Min Price per Guest" value={minPrice} onChange={(e) => setMinPrice(e.target.value)} />
          <input type="number" min="0" placeholder="Max Price per Guest" value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} />
          <button type="button" onClick={() => { setMinPrice(""); setMaxPrice(""); setPriceError(""); }}>Clear</button>
        </div>
        {priceError && <p style={{ color: "red" }}>{priceError}</p>}

        {loading && <p>Loading caterers...</p>}

        {error && (
          <div className="empty-listing">
            <h3>Unable to load caterers</h3>
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && caterers.length === 0 && (
          <div className="empty-listing">
            <h3>No caterers available yet</h3>
            <p>Please check again later.</p>
          </div>
        )}

        {!loading && !error && caterers.length > 0 && (
          <>
            {/* Comparison controls */}
            <div className="comparison-toolbar">
              <p>
                {selectedIds.length} of 3 caterers selected
                for comparison
              </p>

              <button
                type="button"
                className="compare-button"
                onClick={compareCaterers}
                disabled={
                  comparisonLoading ||
                  selectedIds.length < 2
                }
              >
                {comparisonLoading
                  ? "Comparing..."
                  : "Compare Selected"}
              </button>

              <button
                type="button"
                className="clear-comparison-button"
                onClick={clearComparison}
              >
                Clear Selection
              </button>

              {comparisonError && (
                <p className="comparison-error">
                  {comparisonError}
                </p>
              )}
            </div>

            {/* Caterer cards */}
            {filteredCaterers.length > 0 ? (
              <>
                <p>
                  Showing {filteredCaterers.length} of{" "}
                  {caterers.length} caterers
                </p>

                <div className="caterer-list">
                  {filteredCaterers.map((caterer) => (
                    <article
                      className="caterer-card"
                      key={caterer.id}
                    >
                      <div className="caterer-card-content">
                        <label className="compare-checkbox">
                          <input
                            type="checkbox"
                            checked={selectedIds.includes(
                              caterer.id
                            )}
                            onChange={() =>
                              toggleComparison(caterer)
                            }
                          />
                          Add to compare
                        </label>
                      </div>

                      <CatererCard caterer={caterer} />
                    </article>
                  ))}
                </div>
              </>
            ) : (
              <div className="empty-listing">
                <h3>No matching caterers found</h3>
                <p>
                  Try another name, category or location.
                </p>
              </div>
            )}

            {/* Comparison table */}
            {comparisonData.length > 0 && (
              <section className="comparison-section">
                <h2 className="comparison-heading">
                  Compare Catering Services
                </h2>

                <div className="comparison-table-wrapper">
                  <table className="comparison-table">
                    <thead>
                      <tr>
                        <th>Details</th>

                        {comparisonData.map((caterer) => (
                          <th key={caterer.id}>
                            {caterer.business_name}
                          </th>
                        ))}
                      </tr>
                    </thead>

                    <tbody>
                      <tr>
                        <td>Category</td>

                        {comparisonData.map((caterer) => (
                          <td key={caterer.id}>
                            {caterer.category ||
                              "Not specified"}
                          </td>
                        ))}
                      </tr>

                      <tr>
                        <td>Location</td>

                        {comparisonData.map((caterer) => (
                          <td key={caterer.id}>
                            {caterer.location ||
                              "Not specified"}
                          </td>
                        ))}
                      </tr>

                      <tr>
                        <td>Description</td>

                        {comparisonData.map((caterer) => (
                          <td key={caterer.id}>
                            {caterer.description ||
                              "Not provided"}
                          </td>
                        ))}
                      </tr>

                      <tr>
                        <td>Packages</td>

                        {comparisonData.map((caterer) => (
                          <td key={caterer.id}>
                            {caterer.packages?.length ? (
                              <ul>
                                {caterer.packages.map(
                                  (item) => (
                                    <li key={item.id}>
                                      <strong>
                                        {item.package_name}
                                      </strong>
                                      <br />
                                      Price per guest: KSh{" "}
                                      {item.price_per_guest ??
                                        "Not specified"}
                                    </li>
                                  )
                                )}
                              </ul>
                            ) : (
                              "No packages listed"
                            )}
                          </td>
                        ))}
                      </tr>

                      <tr>
                        <td>Menu Items</td>

                        {comparisonData.map((caterer) => (
                          <td key={caterer.id}>
                            {caterer.packages?.some(
                              (item) =>
                                item.menu_items?.length
                            ) ? (
                              <ul>
                                {caterer.packages.flatMap(
                                  (item) =>
                                    (item.menu_items || []).map(
                                      (menuItem) => (
                                        <li
                                          key={`${item.id}-${menuItem.id}`}
                                        >
                                          {menuItem.item_name}
                                        </li>
                                      )
                                    )
                                )}
                              </ul>
                            ) : (
                              "No menu items listed"
                            )}
                          </td>
                        ))}
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>
            )}
          </>
        )}
      </section>
    </main>
  );
}

export default BrowseCaterers;
