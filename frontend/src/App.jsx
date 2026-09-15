import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000/api";

function App() {
  const [tenants, setTenants] = useState([]);
  const [selectedTenant, setSelectedTenant] = useState("");
  const [discrepancies, setDiscrepancies] = useState([]);
  const [reason, setReason] = useState("");
  const [sort, setSort] = useState("record_ref");
  const [order, setOrder] = useState("asc");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Load tenants when the application starts.
  useEffect(() => {
    fetch(`${API_URL}/tenants/`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Unable to load tenants.");
        }

        return response.json();
      })
      .then((data) => {
        setTenants(data.tenants || []);

        if (data.tenants && data.tenants.length > 0) {
          setSelectedTenant(data.tenants[0]);
        }
      })
      .catch((err) => {
        setError(err.message);
      });
  }, []);

  // Load discrepancies whenever tenant/filter/sort changes.
  useEffect(() => {
    if (!selectedTenant) {
      return;
    }

    setLoading(true);
    setError("");

    const params = new URLSearchParams();

    params.set("org_id", selectedTenant);
    params.set("sort", sort);
    params.set("order", order);

    if (reason) {
      params.set("reason", reason);
    }

    fetch(`${API_URL}/discrepancies/?${params.toString()}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Unable to load discrepancies.");
        }

        return response.json();
      })
      .then((data) => {
        setDiscrepancies(data.results || []);
      })
      .catch((err) => {
        setError(err.message);
        setDiscrepancies([]);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [selectedTenant, reason, sort, order]);

  function changeSort(field) {
    if (sort === field) {
      setOrder(order === "asc" ? "desc" : "asc");
    } else {
      setSort(field);
      setOrder("asc");
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Cross-System Reconciliation</h1>
        <p>
          Review discrepancies between System A and System B.
        </p>
      </header>

      <section className="filters">
        <div>
          <label htmlFor="tenant">Tenant</label>

          <select
            id="tenant"
            value={selectedTenant}
            onChange={(event) => setSelectedTenant(event.target.value)}
          >
            {tenants.map((tenant) => (
              <option key={tenant} value={tenant}>
                {tenant}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="reason">Reason</label>

          <select
            id="reason"
            value={reason}
            onChange={(event) => setReason(event.target.value)}
          >
            <option value="">All reasons</option>
            <option value="MISSING_IN_B">
              Missing in System B
            </option>
            <option value="ORPHAN_IN_B">
              Orphan in System B
            </option>
            <option value="DUPLICATE_IN_B">
              Duplicate in System B
            </option>
            <option value="VALUE_MISMATCH">
              Value mismatch
            </option>
          </select>
        </div>

        <div>
          <label htmlFor="sort">Sort by</label>

          <select
            id="sort"
            value={sort}
            onChange={(event) => {
              setSort(event.target.value);
              setOrder("asc");
            }}
          >
            <option value="record_ref">Record</option>
            <option value="reason">Reason</option>
            <option value="system_a_value">
              System A Value
            </option>
            <option value="system_b_value">
              System B Value
            </option>
            <option value="location_id">
              Location
            </option>
          </select>
        </div>

        <button
          type="button"
          onClick={() =>
            setOrder(order === "asc" ? "desc" : "asc")
          }
        >
          {order === "asc" ? "Ascending ↑" : "Descending ↓"}
        </button>
      </section>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {loading ? (
        <p>Loading discrepancies...</p>
      ) : (
        <section>
          <div className="summary">
            <strong>
              {discrepancies.length}
            </strong>{" "}
            discrepancies for{" "}
            <strong>{selectedTenant}</strong>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>
                    <button
                      type="button"
                      onClick={() => changeSort("record_ref")}
                    >
                      Record
                    </button>
                  </th>

                  <th>Location</th>

                  <th>
                    <button
                      type="button"
                      onClick={() => changeSort("reason")}
                    >
                      Reason
                    </button>
                  </th>

                  <th>
                    <button
                      type="button"
                      onClick={() =>
                        changeSort("system_a_value")
                      }
                    >
                      System A Value
                    </button>
                  </th>

                  <th>
                    <button
                      type="button"
                      onClick={() =>
                        changeSort("system_b_value")
                      }
                    >
                      System B Value
                    </button>
                  </th>
                </tr>
              </thead>

              <tbody>
                {discrepancies.length === 0 ? (
                  <tr>
                    <td colSpan="5">
                      No discrepancies found.
                    </td>
                  </tr>
                ) : (
                  discrepancies.map((item) => (
                    <tr key={item.id}>
                      <td>{item.record_ref}</td>

                      <td>
                        {item.location_id}
                        <br />
                        <small>{item.org_id}</small>
                      </td>

                      <td>{item.reason}</td>

                      <td>
                        {item.system_a_value || "—"}
                      </td>

                      <td>
                        {item.system_b_value || "—"}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}

export default App;