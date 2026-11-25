import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getCatererById, getCaterers } from "../../api";
import Button from "../../components/Button";

function CatererProfile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [caterer, setCaterer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        if (id) {
          const data = await getCatererById(id);
          setCaterer(data.caterer || data);
        } else {
          const list = await getCaterers();
          const arr = Array.isArray(list) ? list : list.caterers || [];
          setCaterer(arr[0] || null);
        }
      } catch (e) {
        setCaterer(null);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) return <div className="page-container"><p>Loading caterer...</p></div>;
  if (!caterer) return <div className="page-container"><p>Caterer not found.</p></div>;

  const name = caterer.business_name || caterer.businessName || "Caterer";
  const location = caterer.location || "";
  const description = caterer.description || "";
  const phone = caterer.contact_number || caterer.phone || "";

  return (
    <div className="page-container">
      <h1>{name}</h1>
      <p><strong>Location:</strong> {location}</p>
      {phone && <p><strong>Phone:</strong> {phone}</p>}
      <p>{description}</p>
      <Button onClick={() => navigate("/booking")}>Book This Caterer</Button>
    </div>
  );
}

export default CatererProfile;