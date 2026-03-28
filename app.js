let currentStore = "costco";
let currentCategory = "All";

const sidebar = document.getElementById("sidebar");
const content = document.getElementById("content");
const overlay = document.getElementById("overlay");
const modal = document.getElementById("productModal");
const menuToggle = document.getElementById("menuToggle");
const searchInput = document.getElementById("searchInput");
const sortSelect = document.getElementById("sortSelect");

// Returns the best available image HTML for a product.
// Priority: 1) video capture  2) web search image  3) emoji fallback
function getProductImageHTML(product, size) {
    if (product.image) {
        return `<img src="${product.image}" alt="${product.name}" style="width:100%;height:100%;object-fit:cover;">`;
    }
    if (product.imageUrl) {
        return `<img src="${product.imageUrl}" alt="${product.name}" style="width:100%;height:100%;object-fit:cover;" onerror="this.outerHTML='${product.emoji}'">`;
    }
    return product.emoji;
}

// Returns a label describing the image source
function getImageSourceLabel(product) {
    if (product.image) return "📹 Captured from video";
    if (product.imageUrl) return "🔍 Retrieved from web search";
    return "🏷️ Emoji placeholder (no image available)";
}

// Sidebar toggle
menuToggle.addEventListener("click", () => {
    if (window.innerWidth <= 768) {
        sidebar.classList.toggle("open");
        overlay.classList.toggle("active");
    } else {
        sidebar.classList.toggle("collapsed");
        content.classList.toggle("expanded");
    }
});

// Store selection
document.querySelectorAll(".store-item").forEach(item => {
    item.addEventListener("click", () => {
        document.querySelectorAll(".store-item").forEach(i => i.classList.remove("active"));
        item.classList.add("active");
        currentStore = item.dataset.store;
        currentCategory = "All";
        searchInput.value = "";
        renderStore();
        if (window.innerWidth <= 768) {
            sidebar.classList.remove("open");
            overlay.classList.remove("active");
        }
    });
});

// Search
searchInput.addEventListener("input", () => {
    renderProducts();
});

// Sort
sortSelect.addEventListener("change", () => {
    renderProducts();
});

// Overlay click
overlay.addEventListener("click", () => {
    closeModal();
    if (document.getElementById("uploadModal").classList.contains("active")) {
        closeUploadModal();
    }
    if (window.innerWidth <= 768) {
        sidebar.classList.remove("open");
        overlay.classList.remove("active");
    }
});

// Modal close
document.getElementById("modalClose").addEventListener("click", closeModal);

function renderStore() {
    const info = storeInfo[currentStore];
    document.getElementById("storeName").textContent = info.name;
    document.getElementById("storeDesc").textContent = info.desc;

    const banner = document.getElementById("storeBanner");
    banner.style.background = `linear-gradient(135deg, ${info.color}, ${adjustColor(info.color, 40)})`;

    renderCategories();
    renderProducts();
}

function renderCategories() {
    const items = products[currentStore] || [];
    const categories = ["All", ...new Set(items.map(p => p.category))];
    const container = document.getElementById("categoryTabs");

    container.innerHTML = categories.map(cat =>
        `<button class="category-tab ${cat === currentCategory ? 'active' : ''}" data-cat="${cat}">${cat}</button>`
    ).join("");

    container.querySelectorAll(".category-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            currentCategory = tab.dataset.cat;
            container.querySelectorAll(".category-tab").forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            renderProducts();
        });
    });
}

function renderProducts() {
    let items = [...(products[currentStore] || [])];

    // Filter by category
    if (currentCategory !== "All") {
        items = items.filter(p => p.category === currentCategory);
    }

    // Filter by search
    const query = searchInput.value.trim().toLowerCase();
    if (query) {
        items = items.filter(p =>
            p.name.toLowerCase().includes(query) ||
            p.category.toLowerCase().includes(query) ||
            p.desc.toLowerCase().includes(query)
        );
    }

    // Sort
    const sort = sortSelect.value;
    if (sort === "price-asc") items.sort((a, b) => a.price - b.price);
    else if (sort === "price-desc") items.sort((a, b) => b.price - a.price);
    else items.sort((a, b) => a.name.localeCompare(b.name));

    // Update count
    document.getElementById("productCount").textContent = `${items.length} products`;

    const grid = document.getElementById("productGrid");
    const AD_INTERVAL = 8; // insert an in-feed ad every 8 products
    let html = "";
    items.forEach((p, i) => {
        // Insert in-feed ad after every AD_INTERVAL products
        if (i > 0 && i % AD_INTERVAL === 0) {
            html += `
            <div class="ad-infeed">
                <div>
                    <div class="ad-label">Sponsored</div>
                    <ins class="adsbygoogle"
                         style="display:block"
                         data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
                         data-ad-slot="INFEED_AD_SLOT"
                         data-ad-format="fluid"
                         data-ad-layout-key="INFEED_LAYOUT_KEY"></ins>
                </div>
            </div>`;
        }
        html += `
        <div class="product-card" data-id="${p.id}">
            <div class="product-image">
                ${getProductImageHTML(p)}
                ${p.badge ? `<span class="product-badge">${p.badge}</span>` : ''}
            </div>
            <div class="product-info">
                <div class="product-name">${p.name}</div>
                <div class="product-unit">${p.unit}</div>
                <div class="product-price">
                    <span class="currency">$</span>${p.price.toFixed(2)}
                </div>
            </div>
        </div>`;
    });
    grid.innerHTML = html;

    // Push in-feed ads to AdSense
    grid.querySelectorAll('.ad-infeed ins.adsbygoogle').forEach(() => {
        try { (adsbygoogle = window.adsbygoogle || []).push({}); } catch(e) {}
    });

    grid.querySelectorAll(".product-card").forEach(card => {
        card.addEventListener("click", () => {
            const product = items.find(p => p.id === parseInt(card.dataset.id));
            if (product) openModal(product);
        });
    });
}

function getCategorySourceLabel(product) {
    if (product._categorySource === "image") return "classified by image recognition";
    return "classified by product name";
}

function openModal(product) {
    const modalImg = document.getElementById("modalImage");
    modalImg.innerHTML = getProductImageHTML(product, "large");

    document.getElementById("modalStore").textContent = storeInfo[currentStore].name;
    document.getElementById("modalName").textContent = product.name;
    document.getElementById("modalDesc").textContent = product.desc;
    document.getElementById("modalPrice").textContent = `$${product.price.toFixed(2)}`;
    document.getElementById("modalUnit").textContent = `Size: ${product.unit}`;
    document.getElementById("modalCategory").textContent = `Category: ${product.category} (${getCategorySourceLabel(product)})`;
    document.getElementById("modalImageSource").textContent = getImageSourceLabel(product);
    document.getElementById("modalShelfInfo").textContent = product.shelf;

    modal.classList.add("active");
    overlay.classList.add("active");
}

function closeModal() {
    modal.classList.remove("active");
    overlay.classList.remove("active");
}

function adjustColor(hex, amount) {
    hex = hex.replace('#', '');
    const r = Math.min(255, parseInt(hex.substring(0, 2), 16) + amount);
    const g = Math.min(255, parseInt(hex.substring(2, 4), 16) + amount);
    const b = Math.min(255, parseInt(hex.substring(4, 6), 16) + amount);
    return `rgb(${r}, ${g}, ${b})`;
}

// ============================================================
// Upload Modal
// ============================================================
const uploadModal = document.getElementById("uploadModal");
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const uploadPreview = document.getElementById("uploadPreview");
const previewMedia = document.getElementById("previewMedia");
const analyzeBtn = document.getElementById("analyzeBtn");
const uploadProgress = document.getElementById("uploadProgress");
const progressFill = document.getElementById("progressFill");
const progressText = document.getElementById("progressText");
const uploadResult = document.getElementById("uploadResult");
let selectedFile = null;
let uploadTargetStore = "costco";
let priceTagPosition = "below"; // "below" or "above"

const storeEmojis = {
    costco: "🏬", "sams-club": "🏪", walmart: "🛒",
    "traders-joe": "🌿", kroger: "🛍️"
};

// Open upload modal for a specific store
function openUploadModal(storeKey) {
    uploadTargetStore = storeKey;
    document.getElementById("uploadStoreSelect").value = storeKey;
    updateUploadStoreUI(storeKey);
    uploadModal.classList.add("active");
    overlay.classList.add("active");
}

// Update the modal header and pills to reflect selected store
function updateUploadStoreUI(storeKey) {
    const info = storeInfo[storeKey];
    document.getElementById("uploadStoreIcon").textContent = storeEmojis[storeKey] || "🏬";
    document.getElementById("uploadStoreTitle").textContent = `Upload for ${info.name}`;
    document.getElementById("uploadStoreName").textContent = info.name;

    // Update header gradient color
    const header = document.getElementById("uploadStoreHeader");
    header.style.background = `linear-gradient(135deg, ${info.color}, ${adjustColor(info.color, 40)})`;

    // Update pills
    document.querySelectorAll(".store-pill").forEach(pill => {
        pill.classList.toggle("active", pill.dataset.store === storeKey);
    });
}

// Sidebar bottom upload button — opens modal for current store
document.getElementById("uploadBtn").addEventListener("click", () => {
    openUploadModal(currentStore);
});

// Banner upload button — opens modal for current store
document.getElementById("bannerUploadBtn").addEventListener("click", () => {
    openUploadModal(currentStore);
});

// Sidebar per-store upload buttons
document.querySelectorAll(".store-upload-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
        e.stopPropagation(); // don't trigger store selection
        openUploadModal(btn.dataset.store);
    });
});

// Store pills inside upload modal — switch target store
document.querySelectorAll(".store-pill").forEach(pill => {
    pill.addEventListener("click", () => {
        uploadTargetStore = pill.dataset.store;
        document.getElementById("uploadStoreSelect").value = pill.dataset.store;
        updateUploadStoreUI(pill.dataset.store);
    });
});

// Price tag position buttons
document.querySelectorAll(".price-tag-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".price-tag-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        priceTagPosition = btn.dataset.position;
    });
});

// Close upload modal
document.getElementById("uploadModalClose").addEventListener("click", () => {
    closeUploadModal();
});

function closeUploadModal() {
    uploadModal.classList.remove("active");
    overlay.classList.remove("active");
    resetUploadUI();
}

function resetUploadUI() {
    selectedFile = null;
    dropZone.style.display = "";
    uploadPreview.style.display = "none";
    uploadProgress.style.display = "none";
    uploadResult.style.display = "none";
    document.getElementById("priceTagPosition").style.display = "none";
    priceTagPosition = "below";
    document.querySelectorAll(".price-tag-btn").forEach(b => {
        b.classList.toggle("active", b.dataset.position === "below");
    });
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyze Shelf";
    progressFill.className = "progress-fill";
    progressFill.style.width = "0%";
}

// Drag & Drop
dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    if (e.dataTransfer.files.length > 0) {
        handleFile(e.dataTransfer.files[0]);
    }
});

// Browse Files button opens file picker (not the whole drop zone, to avoid double-trigger)
document.getElementById("filePickerBtn").addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.click();
});

// File input change
fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        handleFile(fileInput.files[0]);
    }
});

// Remove file
document.getElementById("removeFileBtn").addEventListener("click", () => {
    resetUploadUI();
});

function handleFile(file) {
    const validExtensions = [
        ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff",
        ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"
    ];
    const ext = file.name.toLowerCase().slice(file.name.lastIndexOf("."));
    const isValidType = file.type.startsWith("image/") || file.type.startsWith("video/");
    const isValidExt = validExtensions.includes(ext);

    if (!isValidType && !isValidExt) {
        showToast("Unsupported file format");
        return;
    }

    if (file.size > 200 * 1024 * 1024) {
        showToast("File too large (max 200MB)");
        return;
    }

    selectedFile = file;

    // Show preview
    dropZone.style.display = "none";
    uploadPreview.style.display = "flex";
    document.getElementById("fileName").textContent = file.name;
    document.getElementById("fileSize").textContent = formatFileSize(file.size);

    const url = URL.createObjectURL(file);
    const videoExts = [".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"];
    const isVideo = file.type.startsWith("video/") || videoExts.includes(ext);
    if (isVideo) {
        previewMedia.innerHTML = `<video src="${url}" muted></video>`;
    } else {
        previewMedia.innerHTML = `<img src="${url}" alt="Preview">`;
    }

    analyzeBtn.disabled = false;

    // Show price tag position selector
    document.getElementById("priceTagPosition").style.display = "block";
}

// Analyze button
analyzeBtn.addEventListener("click", async () => {
    if (!selectedFile) return;

    const store = uploadTargetStore;
    const storeName = storeInfo[store]?.name || store;

    // Show progress
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = `Analyzing ${storeName}...`;
    uploadProgress.style.display = "block";
    uploadResult.style.display = "none";
    progressFill.classList.add("indeterminate");
    progressText.textContent = `Uploading to ${storeName}...`;

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("store", store);
    formData.append("price_tag_position", priceTagPosition);

    try {
        progressText.textContent = `AI is analyzing ${storeName} shelf products...`;

        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || `Server error: ${response.status}`);
        }

        const result = await response.json();

        // Stop progress animation
        progressFill.classList.remove("indeterminate");
        progressFill.style.width = "100%";

        const storeKey = result.store;

        if (result.products.length === 0) {
            showUploadResult(false, "No products detected. Try a clearer image.");
            return;
        }

        // Merge new products into the store data
        if (!products[storeKey]) {
            products[storeKey] = [];
        }

        // Find max existing ID
        const maxId = products[storeKey].reduce((max, p) => Math.max(max, p.id || 0), 0);

        let addedCount = 0;
        result.products.forEach((p, i) => {
            // Check for duplicate names
            const exists = products[storeKey].some(
                existing => existing.name.toLowerCase() === p.name.toLowerCase()
            );
            if (!exists) {
                const newProduct = {
                    id: maxId + i + 1,
                    name: p.name,
                    price: p.price || 0,
                    unit: p.unit || "",
                    emoji: p.emoji || "📦",
                    image: p.image || null,
                    imageUrl: p.imageUrl || null,
                    desc: p.desc || "",
                    shelf: p.shelf || "",
                    badge: "NEW",
                };
                // Auto-classify category
                const classified = classifyProduct(newProduct);
                newProduct.category = classified.category;
                newProduct._categorySource = classified.source;

                products[storeKey].push(newProduct);
                addedCount++;
            }
        });

        // Switch to the target store page and re-render
        currentStore = storeKey;
        currentCategory = "All";
        searchInput.value = "";
        document.querySelectorAll(".store-item").forEach(item => {
            item.classList.toggle("active", item.dataset.store === storeKey);
        });

        renderStore();

        const timeStr = result.processing_time_seconds.toFixed(1);
        showUploadResult(
            true,
            `${addedCount} new products added to ${storeInfo[storeKey].name} (${result.frames_analyzed} frame(s), ${timeStr}s)`
        );

        // Close modal after short delay and navigate to the store page
        setTimeout(() => {
            closeUploadModal();
            showToast(`${addedCount} new products added to ${storeInfo[storeKey].name}`);
        }, 1500);

    } catch (error) {
        progressFill.classList.remove("indeterminate");
        showUploadResult(false, error.message);
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Retry";
    }
});

function showUploadResult(success, message) {
    uploadResult.style.display = "block";
    uploadResult.className = "upload-result" + (success ? "" : " error");
    document.getElementById("resultIcon").textContent = success ? "✅" : "❌";
    document.getElementById("resultText").textContent = message;
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

// Toast notification
function showToast(message) {
    let toast = document.querySelector(".toast");
    if (!toast) {
        toast = document.createElement("div");
        toast.className = "toast";
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 3000);
}

// Keyboard shortcut - Escape to close modals
document.addEventListener("keydown", e => {
    if (e.key === "Escape") {
        closeModal();
        if (uploadModal.classList.contains("active")) closeUploadModal();
    }
});

// Load saved products from server, merge with defaults, then render
async function loadSavedProducts() {
    try {
        const resp = await fetch("/api/products");
        if (!resp.ok) return;
        const saved = await resp.json();

        for (const [storeKey, savedItems] of Object.entries(saved)) {
            if (!products[storeKey]) {
                products[storeKey] = [];
            }
            const existingNames = new Set(
                products[storeKey].map(p => p.name.toLowerCase().trim())
            );
            const maxId = products[storeKey].reduce((max, p) => Math.max(max, p.id || 0), 0);
            let nextId = maxId;

            for (const sp of savedItems) {
                const nameKey = (sp.name || "").toLowerCase().trim();
                if (!nameKey || existingNames.has(nameKey)) continue;
                nextId++;
                sp.id = nextId;
                // Auto-classify
                const classified = classifyProduct(sp);
                sp.category = classified.category;
                sp._categorySource = classified.source;
                products[storeKey].push(sp);
                existingNames.add(nameKey);
            }
        }
    } catch (e) {
        console.log("No saved products found, using defaults");
    }

    classifyAllProducts();
    renderStore();
}

loadSavedProducts();
