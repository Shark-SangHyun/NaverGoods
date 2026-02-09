(() => {
  const $ = (id) => document.getElementById(id);

  const skuInput = $("sku");
  const btn = $("btnDetect");
  const result = $("result");

  const productNameInput = $("productName");
  const productGroupInput = $("productGroup");

  const categoryQueryInput = $("categoryQuery");
  const teeTypeWrap = $("teeTypeWrap");
  const teeTypeSelect = $("teeType");
  const btnApplyCategory = $("btnApplyCategory");

  const priceOriginalInput = $("priceOriginal");
  const priceSaleInput = $("priceSale");
  const priceDiffInput = $("priceDiff");

  const originCountryInput = $("originCountry");
  const manufactureDateInput = $("manufactureDate");

  const MAP_AGE = { D: "아이더 성인", J: "아이더 아동" };
  const MAP_GENDER = { M: "남성", W: "여성", U: "공용" };
  const MAP_GENDER_NAME = { M: "남자", W: "여자", U: "남여공용" };
  const MAP_SEASON = {
    P: "봄",
    M: "여름",
    U: "가을",
    W: "겨울",
    S: "S/S",
    F: "F/W",
    A: "ALL",
  };

  const MAP_ITEM = {
    "1": "자켓",
    "2": "티셔츠",
    "3": "바지",
    "4": "셔츠",
    "5": "다운(패딩)",
    "6": "베스트(조끼)",
    "7": "고어택스",
    "8": "속옷",
    "9": "용품",
    A: "캠핑",
    B: "가방",
    C: "모자",
    S: "양말",
    T: "스틱",
    V: "장갑",
    M: "SET(티/바지)",
    G: "고어택스신발",
    N: "일반신발",
  };

  function lineToGroup(lineNumber) {
    if (lineNumber >= 1 && lineNumber <= 40) return "M";
    if (lineNumber >= 41 && lineNumber <= 80) return "C";
    if (lineNumber >= 81 && lineNumber <= 99) return "P";
    return null;
  }

  function classifyProductGroup(itemCode) {
    const code = String(itemCode || "").toUpperCase();

    if (["1", "2", "3", "4", "5", "6", "7", "8", "M"].includes(code)) return "의류";
    if (["N", "G"].includes(code)) return "구두/신발";
    if (code === "B") return "가방";
    if (["A", "T"].includes(code)) return "스포츠용품";
    return "패션잡화";
  }

  function categoryPathByItemCode(itemCode, teeType) {
    const code = String(itemCode || "").toUpperCase();

    const MAP = {
      "1": "스포츠/레저>등산>등산의류>재킷",
      "5": "스포츠/레저>등산>등산의류>점퍼",
      "3": "스포츠/레저>등산>등산의류>바지",
      "6": "스포츠/레저>등산>등산의류>조끼",
      "8": "스포츠/레저>등산>등산의류>기능성언더웨어",
      "G": "스포츠/레저>등산>등산화",
      "N": "스포츠/레저>등산>등산화",
      "B": "스포츠/레저>등산>등산가방",
      "C": "스포츠/레저>등산>등산잡화>모자",
      "S": "스포츠/레저>등산>등산잡화>양말",
      "V": "스포츠/레저>등산>등산잡화>장갑",
      "T": "스포츠/레저>등산>등산장비>스틱",
    };

    if (code === "2") {
      return teeType === "short"
        ? "스포츠/레저>등산>등산의류>반팔티셔츠"
        : "스포츠/레저>등산>등산의류>긴팔티셔츠";
    }

    return MAP[code] || "";
  }

  function parseSku(raw) {
    const s = String(raw || "").trim().toUpperCase();
    if (s.length !== 8) return { ok: false, error: "품번은 8자리로 입력해야 합니다." };

    const ageCode = s[0];
    const genderCode = s[1];
    const seasonCode = s[2];
    const yearCode = s.slice(3, 5);
    const itemCode = s[5];
    const lineCode = s.slice(6, 8);

    if (!/^\d{2}$/.test(yearCode)) return { ok: false, error: "연도 구분(4번)은 숫자 2자리여야 합니다. (예: 26)" };
    if (!/^\d{2}$/.test(lineCode)) return { ok: false, error: "라인 구분(6번)은 숫자 2자리여야 합니다. (예: 01~99)" };

    if (!MAP_AGE[ageCode]) return { ok: false, error: "연령 구분(1번)이 올바르지 않습니다. (D/J)" };
    if (!MAP_GENDER[genderCode]) return { ok: false, error: "성별 구분(2번)이 올바르지 않습니다. (M/W/U)" };
    if (!MAP_SEASON[seasonCode]) return { ok: false, error: "시즌 구분(3번)이 올바르지 않습니다. (P/M/U/W/S/F/A)" };
    if (!MAP_ITEM[itemCode]) return { ok: false, error: "아이템 구분(5번)이 올바르지 않습니다." };

    const yearNum = Number(yearCode);
    const fullYear = 2000 + yearNum;

    const lineNum = Number(lineCode);
    if (lineNum < 1 || lineNum > 99) return { ok: false, error: "라인 구분(6번)은 01~99 범위여야 합니다." };

    const lineGroup = lineToGroup(lineNum);
    if (!lineGroup) return { ok: false, error: "라인 구분(6번)이 범위를 벗어났습니다." };

    return {
      ok: true,
      normalized: s,
      parts: {
        "1. 연령": { code: ageCode, value: MAP_AGE[ageCode] },
        "2. 성별": { code: genderCode, value: MAP_GENDER[genderCode] },
        "3. 시즌": { code: seasonCode, value: MAP_SEASON[seasonCode] },
        "4. 연도": { code: yearCode, value: `${fullYear}년도` },
        "5. 아이템": { code: itemCode, value: MAP_ITEM[itemCode] },
        "6. 라인": {
          code: lineCode,
          value: `${String(lineNum).padStart(2, "0")} (구분: ${lineGroup})`,
        },
      },
      meta: {
        genderName: MAP_GENDER_NAME[genderCode],
        itemCode,
      },
    };
  }

  function buildProductName(parsed) {
    return `아이더 ${parsed.meta.genderName} ${parsed.normalized}`;
  }

  function renderResult(parsed) {
    if (!parsed.ok) {
      result.textContent = `❌ 잘못 입력되었습니다.\n- ${parsed.error}\n\n예시: DMU26101`;
      return;
    }

    const lines = [`✅ 식별 완료: ${parsed.normalized}`, ""];
    for (const [k, v] of Object.entries(parsed.parts)) lines.push(`${k}  ${v.code}  →  ${v.value}`);
    result.textContent = lines.join("\n");
  }

  function runDetect() {
    const parsed = parseSku(skuInput.value);
    renderResult(parsed);
    if (!parsed.ok) return;

    if (productNameInput) productNameInput.value = buildProductName(parsed);
    if (productGroupInput) productGroupInput.value = classifyProductGroup(parsed.meta.itemCode);

    const isTee = String(parsed.meta.itemCode || "").toUpperCase() === "2";
    if (teeTypeWrap) teeTypeWrap.style.display = isTee ? "" : "none";

    const teeType = teeTypeSelect ? teeTypeSelect.value : "long";
    const path = categoryPathByItemCode(parsed.meta.itemCode, teeType);
    if (categoryQueryInput && path) categoryQueryInput.value = path;
  }

  // ---- 가격 차액 자동 계산 ----
  function onlyNumberText(s) {
    return String(s || "").replace(/[^\d]/g, "");
  }

  function formatKRW(n) {
    if (!Number.isFinite(n)) return "";
    return n.toLocaleString("ko-KR");
  }

  function calcPriceDiff() {
    if (!priceOriginalInput || !priceSaleInput || !priceDiffInput) return;

    const original = Number(onlyNumberText(priceOriginalInput.value));
    const sale = Number(onlyNumberText(priceSaleInput.value));

    if (!original && !sale) {
      priceDiffInput.value = "";
      return;
    }

    const diff = original - sale;
    priceDiffInput.value = `${formatKRW(diff)}원`;
  }

  // ---- 이벤트 연결 ----
  if (btn) btn.addEventListener("click", runDetect);
  if (skuInput) {
    skuInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") btn?.click();
    });
  }

  if (teeTypeSelect) {
    teeTypeSelect.addEventListener("change", () => {
      const parsed = parseSku(skuInput.value);
      if (!parsed.ok) return;
      const path = categoryPathByItemCode(parsed.meta.itemCode, teeTypeSelect.value);
      if (categoryQueryInput && path) categoryQueryInput.value = path;
    });
  }

  if (priceOriginalInput) priceOriginalInput.addEventListener("input", calcPriceDiff);
  if (priceSaleInput) priceSaleInput.addEventListener("input", calcPriceDiff);

  if (btnApplyCategory) {
    btnApplyCategory.addEventListener("click", async () => {
      const q = String(categoryQueryInput?.value || "").trim();
      if (!q) {
        alert("카테고리(네이버) 값을 입력하세요.");
        return;
      }

      try {
        btnApplyCategory.disabled = true;

        const res = await fetch("/api/set-category", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: q }),
        });

        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data?.detail || `HTTP ${res.status}`);

        alert("네이버 카테고리 적용 완료");
      } catch (e) {
        alert(`실패: ${e.message}`);
      } finally {
        btnApplyCategory.disabled = false;
      }
    });
  }
})();
