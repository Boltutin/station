/**
 * WebXR Interactive Passenger Station Pavilion Logic
 * Developed for DVGUPS Coursework in 'Virtual and Augmented Reality Modeling'
 * Student: Boltutin V.V., Group: BZI45TVR
 */

document.addEventListener('DOMContentLoaded', () => {
    const viewer = document.getElementById('stationViewer');
    const infoPanel = document.getElementById('infoPanel');
    const closePanelBtn = document.getElementById('closePanelBtn');
    const infoTitle = document.getElementById('infoTitle');
    const infoDesc = document.getElementById('infoDesc');
    const specStandard = document.getElementById('specStandard');
    const specMaterial = document.getElementById('specMaterial');
    const btnFocusItem = document.getElementById('btnFocusItem');

    const btnResetCamera = document.getElementById('btnResetCamera');
    const btnToggleRotate = document.getElementById('btnToggleRotate');
    const btnToggleHotspots = document.getElementById('btnToggleHotspots');
    const btnToggleTheme = document.getElementById('btnToggleTheme');
    const btnScaleMode = document.getElementById('btnScaleMode');
    const scaleLabel = document.getElementById('scaleLabel');

    const btnQr = document.getElementById('btn-qr');
    const qrModal = document.getElementById('qrModal');
    const closeQrBtn = document.getElementById('closeQrBtn');
    const qrcodeContainer = document.getElementById('qrcode');

    // Initial camera state
    const DEFAULT_ORBIT = '40deg 75deg 26m';
    const DEFAULT_TARGET = '0m 2.0m 1.8m';
    let currentHotspot = null;
    let isDayMode = true;
    let isScaleMockup = true;
    let qrGenerated = false;

    // Component specifications dictionary
    const SPECS_DICT = {
        'Пассажирский павильон ожидания': {
            standard: 'СТО РЖД 03.001-2014',
            material: 'Сталь 09Г2С / Триплекс'
        },
        'Пандус доступной среды (МГН)': {
            standard: 'СП 59.13330.2020',
            material: 'Бетон B25 / AISI 304'
        },
        'Тактильная полоса безопасности': {
            standard: 'ГОСТ Р 52875-2018',
            material: 'Полиуретан сигнальный'
        },
        'Железнодорожный путь колеи 1520 мм': {
            standard: 'ГОСТ Р 51685-2013',
            material: 'Сталь рельсовая Э76Ф'
        },
        'Электронное навигационное табло': {
            standard: 'ГОСТ 33798.1-2016',
            material: 'LED матрица IP65'
        },
        'Опора LED-освещения платформы': {
            standard: 'СП 52.13330.2016',
            material: 'Оцинкованная сталь'
        },
        'Торцевой лестничный сход': {
            standard: 'СП 225.1326000 / СП 59',
            material: 'Бетон B30 / Сталь AISI 304'
        },
        'Станционная навигация ОАО «РЖД»': {
            standard: 'СТО РЖД / СП 59.13330',
            material: 'Сталь 09Г2С / Эмаль РЖД'
        },
        'Колонна экстренной связи «Инфо-SOS»': {
            standard: 'ГОСТ Р 52875 / СТО РЖД',
            material: 'Сталь 09Г2С / LED-маяк'
        }
    };

    // Helper to calculate shortest-arc camera orbit transition
    function parseOrbit(orbitStr) {
        if (!orbitStr) return null;
        const parts = orbitStr.trim().split(/\s+/);
        if (parts.length < 3) return null;
        const theta = parseFloat(parts[0]);
        const phi = parseFloat(parts[1]);
        const radius = parts[2];
        return { theta, phi, radius };
    }

    function calculateOptimalOrbit(targetOrbitStr) {
        const target = parseOrbit(targetOrbitStr);
        if (!target) return targetOrbitStr;

        try {
            const current = viewer.getCameraOrbit();
            if (!current) return targetOrbitStr;

            const curThetaDeg = (current.theta * 180) / Math.PI;
            // Shortest angular path (-180° to +180°)
            const diff = ((target.theta - curThetaDeg) % 360 + 540) % 360 - 180;
            const optimalTheta = curThetaDeg + diff;

            return `${optimalTheta.toFixed(1)}deg ${target.phi}deg ${target.radius}`;
        } catch (e) {
            return targetOrbitStr;
        }
    }

    // =========================================================================
    // Hotspots Interactive Handling
    // =========================================================================
    const hotspots = document.querySelectorAll('.hotspot');
    hotspots.forEach(hotspot => {
        const onHotspotSelect = (e) => {
            e.stopPropagation();
            selectHotspot(hotspot);
        };
        hotspot.addEventListener('click', onHotspotSelect);
        hotspot.addEventListener('touchend', onHotspotSelect);
    });

    function selectHotspot(hotspot) {
        currentHotspot = hotspot;
        const title = hotspot.dataset.title;
        const desc = hotspot.dataset.desc;
        const orbit = hotspot.dataset.orbit;
        const target = hotspot.dataset.target;

        infoTitle.textContent = title;
        infoDesc.textContent = desc;

        const specs = SPECS_DICT[title] || { standard: 'ГОСТ / СП', material: 'Конструкционный PBR' };
        specStandard.textContent = specs.standard;
        specMaterial.textContent = specs.material;

        infoPanel.classList.add('visible');

        // In AR mode, physical camera controls view; do not override camera orbit
        if (!document.body.classList.contains('ar-active')) {
            if (orbit) {
                viewer.cameraOrbit = calculateOptimalOrbit(orbit);
            }
            if (target) {
                viewer.cameraTarget = target;
            }
            viewer.autoRotate = false;
            btnToggleRotate.classList.remove('active');
        }
    }

    const onClosePanel = (e) => {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
            if (e.stopImmediatePropagation) e.stopImmediatePropagation();
        }
        infoPanel.classList.remove('visible');
    };
    closePanelBtn.addEventListener('click', onClosePanel);
    closePanelBtn.addEventListener('touchend', onClosePanel);

    const btnDismissCard = document.getElementById('btnDismissCard');
    if (btnDismissCard) {
        btnDismissCard.addEventListener('click', onClosePanel);
        btnDismissCard.addEventListener('touchend', onClosePanel);
    }

    const onFocusClick = (e) => {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
            if (e.stopImmediatePropagation) e.stopImmediatePropagation();
        }
        if (document.body.classList.contains('ar-active') || viewer.getAttribute('ar-status') === 'object-placed' || viewer.getAttribute('ar-status') === 'session-started') {
            if (currentHotspot && viewer.recenterAROnHotspot) {
                viewer.recenterAROnHotspot(currentHotspot);
            }
        } else {
            if (currentHotspot) {
                selectHotspot(currentHotspot);
            }
        }
    };
    btnFocusItem.addEventListener('click', onFocusClick);
    btnFocusItem.addEventListener('touchend', onFocusClick);

    // =========================================================================
    // Bottom Controls Toolbar
    // =========================================================================
    // 1. Reset Camera
    btnResetCamera.addEventListener('click', () => {
        viewer.cameraOrbit = calculateOptimalOrbit(DEFAULT_ORBIT);
        viewer.cameraTarget = DEFAULT_TARGET;
        infoPanel.classList.remove('visible');
    });

    // 2. Toggle Auto-Rotate
    btnToggleRotate.addEventListener('click', () => {
        viewer.autoRotate = !viewer.autoRotate;
        btnToggleRotate.classList.toggle('active', viewer.autoRotate);
    });

    // 3. Toggle Hotspots Visibility
    btnToggleHotspots.addEventListener('click', () => {
        const isVisible = !btnToggleHotspots.classList.contains('active');
        btnToggleHotspots.classList.toggle('active', isVisible);
        const label = btnToggleHotspots.querySelector('span');
        if (label) {
            label.textContent = isVisible ? 'Метки (9)' : 'Метки (0)';
        }
        hotspots.forEach(h => {
            if (isVisible) {
                h.classList.remove('hidden');
            } else {
                h.classList.add('hidden');
            }
        });
    });

    // =========================================================================
    // Dynamic Snow Particle System (Winter Far Eastern Atmosphere)
    // =========================================================================
    const snowCanvas = document.getElementById('snowCanvas');
    const ctx = snowCanvas.getContext('2d');
    let snowActive = true;
    let flakes = [];
    const FLAKE_COUNT = window.innerWidth < 768 ? 90 : 200;

    function resizeCanvas() {
        snowCanvas.width = window.innerWidth;
        snowCanvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    class Snowflake {
        constructor() {
            this.reset(true);
        }
        reset(randomY = false) {
            this.x = Math.random() * snowCanvas.width;
            this.y = randomY ? Math.random() * snowCanvas.height : -10;
            this.radius = Math.random() * 2.8 + 1.2;
            this.speedY = Math.random() * 1.5 + 0.8;
            this.speedX = Math.random() * 0.6 - 0.3;
            this.swaySpeed = Math.random() * 0.02 + 0.01;
            this.swayAngle = Math.random() * Math.PI * 2;
            this.opacity = Math.random() * 0.7 + 0.3;
        }
        update() {
            this.y += this.speedY;
            this.swayAngle += this.swaySpeed;
            this.x += Math.sin(this.swayAngle) * 0.8 + this.speedX;

            if (this.y > snowCanvas.height + 10) {
                this.reset(false);
            }
            if (this.x < -10) this.x = snowCanvas.width + 10;
            if (this.x > snowCanvas.width + 10) this.x = -10;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(240, 246, 255, ${this.opacity})`;
            ctx.shadowBlur = 4;
            ctx.shadowColor = 'rgba(255, 255, 255, 0.6)';
            ctx.fill();
        }
    }

    for (let i = 0; i < FLAKE_COUNT; i++) {
        flakes.push(new Snowflake());
    }

    function animateSnow() {
        if (snowActive) {
            ctx.clearRect(0, 0, snowCanvas.width, snowCanvas.height);
            for (let flake of flakes) {
                flake.update();
                flake.draw();
            }
        }
        requestAnimationFrame(animateSnow);
    }
    requestAnimationFrame(animateSnow);

    // Adaptive AR Handler: scale model to tabletop size (1:20) so the entire 22m station fits in room/desk!
    // Adaptive AR Handler: Clean camera view, seamless plane detection and responsive controls
    let arHotspotsVisible = true;

    // Check secure HTTPS context on mobile when launching AR
    const arFloatingBtn = document.getElementById('ar-button');
    if (arFloatingBtn) {
        arFloatingBtn.addEventListener('click', (e) => {
            if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
                const proceed = confirm("Для активации дополненной реальности (AR) с камерой браузер требует защищенный протокол HTTPS.\n\nПерейти на официальную онлайн-версию GitHub Pages?");
                if (proceed) {
                    e.preventDefault();
                    e.stopPropagation();
                    window.location.href = "https://boltutin.github.io/station/";
                }
            }
        });
    }

    viewer.addEventListener('ar-status', (event) => {
        if (event.detail.status === 'session-started') {
            document.body.classList.add('ar-active');
            snowActive = false;
            ctx.clearRect(0, 0, snowCanvas.width, snowCanvas.height);
            viewer.style.background = 'transparent';
            viewer.autoRotate = false;
            viewer.exposure = 1.8; // Boost brightness in indoor ambient light

            // Clean AR view: hide hotspots by default so model is unobstructed
            viewer.classList.add('ar-hotspots-hidden');
            viewer.classList.remove('ar-hotspots-shown');
            arHotspotsVisible = false;
            if (viewer.setARHotspotsVisible) {
                viewer.setARHotspotsVisible(false);
            }
            if (arModeText) arModeText.textContent = 'Режим: Перемещение';
            if (arModeIcon) arModeIcon.innerHTML = '<path d="M5 9l-3 3 3 3M9 5l3-3 3 3M15 19l-3 3-3-3M19 9l3 3-3 3M2 12h20M12 2v20"/>';
            if (arHotspotsText) arHotspotsText.textContent = 'Метки: Выкл';
            if (arScaleText) arScaleText.textContent = '1:10 (2.2 м)';
        } else if (event.detail.status === 'object-placed') {
            console.log('WebXR Station Pavilion placed successfully on floor plane.');
        } else if (event.detail.status === 'not-presenting') {
            document.body.classList.remove('ar-active');
            snowActive = isWinterSeason;
            viewer.scale = '1 1 1';
            viewer.exposure = isDayMode ? 1.0 : 0.4;
            viewer.style.background = isDayMode
                ? 'radial-gradient(circle at 50% 30%, #1e2632 0%, #0d1117 75%)'
                : 'radial-gradient(circle at 50% 30%, #090d16 0%, #020408 85%)';
            viewer.autoRotate = true;
            viewer.classList.remove('ar-hotspots-hidden');
            viewer.classList.remove('ar-hotspots-shown');
            arHotspotsVisible = true;
            if (viewer.setARHotspotsVisible) {
                viewer.setARHotspotsVisible(true);
            }
            if (arHotspotsText) arHotspotsText.textContent = 'Метки: Вкл';
        }
    });

    // Direct Tap-to-Anchor bridge for mobile WebXR DOM Overlay
    const onArScreenTapToAnchor = (e) => {
        if (!document.body.classList.contains('ar-active')) return;
        if (e.target && e.target.closest && e.target.closest('button, .ar-pill-btn, #arControlsPill, .hotspot, #infoPanel, aside')) return;
        if (viewer.anchorAR) {
            viewer.anchorAR();
        }
    };
    viewer.addEventListener('click', onArScreenTapToAnchor);
    viewer.addEventListener('touchend', onArScreenTapToAnchor);

    // In-AR Pill controls: Toggle between Move (Перемещение) and Rotate (Вращение)
    const btnArModeToggle = document.getElementById('btnArModeToggle') || document.getElementById('btnArReanchor');
    const arModeText = document.getElementById('arModeText');
    const arModeIcon = document.getElementById('arModeIcon');
    if (btnArModeToggle) {
        btnArModeToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            if (viewer.toggleARInteractionMode) {
                const newMode = viewer.toggleARInteractionMode();
                if (newMode === 'rotate') {
                    if (arModeText) arModeText.textContent = 'Режим: Вращение';
                    if (arModeIcon) arModeIcon.innerHTML = '<path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>';
                } else {
                    if (arModeText) arModeText.textContent = 'Режим: Перемещение';
                    if (arModeIcon) arModeIcon.innerHTML = '<path d="M5 9l-3 3 3 3M9 5l3-3 3 3M15 19l-3 3-3-3M19 9l3 3-3 3M2 12h20M12 2v20"/>';
                }
            } else if (viewer.reanchorAR) {
                viewer.reanchorAR();
            }
        });
    }

    const btnArToggleHotspots = document.getElementById('btnArToggleHotspots');
    const arHotspotsText = document.getElementById('arHotspotsText');
    if (btnArToggleHotspots) {
        btnArToggleHotspots.addEventListener('click', (e) => {
            e.stopPropagation();
            arHotspotsVisible = !arHotspotsVisible;
            viewer.classList.toggle('ar-hotspots-hidden', !arHotspotsVisible);
            viewer.classList.toggle('ar-hotspots-shown', arHotspotsVisible);
            if (viewer.setARHotspotsVisible) {
                viewer.setARHotspotsVisible(arHotspotsVisible);
            }
            arHotspotsText.textContent = arHotspotsVisible ? 'Метки: Вкл' : 'Метки: Выкл';
        });
    }

    const btnArScaleToggle = document.getElementById('btnArScaleToggle');
    const arScaleText = document.getElementById('arScaleText');
    if (btnArScaleToggle) {
        btnArScaleToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            if (viewer.toggleARScale) {
                const newScale = viewer.toggleARScale();
                if (newScale > 0.5) {
                    arScaleText.textContent = '1:1 (22 м)';
                } else if (newScale > 0.08) {
                    arScaleText.textContent = '1:10 (2.2 м)';
                } else {
                    arScaleText.textContent = '1:20 (1.1 м)';
                }
            }
        });
    }

    // =========================================================================
    // Proposal 2: Live Digital Clock & Weather Telemetry
    // =========================================================================
    const liveClockEl = document.getElementById('liveClock');
    const liveTempEl = document.getElementById('liveTemp');

    function updateLiveClock() {
        const now = new Date();
        const hrs = String(now.getHours()).padStart(2, '0');
        const mins = String(now.getMinutes()).padStart(2, '0');
        const secs = String(now.getSeconds()).padStart(2, '0');
        if (liveClockEl) {
            liveClockEl.textContent = `${hrs}:${mins}:${secs}`;
        }
    }
    setInterval(updateLiveClock, 1000);
    updateLiveClock();

    // =========================================================================
    // Proposal 3: Season Switcher (Winter / Summer)
    // =========================================================================
    const btnSeason = document.getElementById('btnSeason');
    const seasonLabel = document.getElementById('seasonLabel');
    let isWinterSeason = true;

    function applySeason(winter) {
        isWinterSeason = winter;
        snowActive = winter;
        snowCanvas.classList.toggle('hidden', !winter);
        btnSeason.classList.toggle('active', winter);
        
        if (winter) {
            seasonLabel.textContent = 'Сезон: Зима';
            if (liveTempEl) liveTempEl.textContent = '-14°C';
            viewer.exposure = isDayMode ? 0.95 : 0.38;
            viewer.style.background = isDayMode
                ? 'radial-gradient(circle at 50% 30%, #1e2632 0%, #0d1117 75%)'
                : 'radial-gradient(circle at 50% 30%, #090d16 0%, #020408 85%)';
        } else {
            seasonLabel.textContent = 'Сезон: Лето';
            if (liveTempEl) liveTempEl.textContent = '+24°C';
            viewer.exposure = isDayMode ? 1.20 : 0.42;
            viewer.style.background = isDayMode
                ? 'radial-gradient(circle at 50% 30%, #243447 0%, #0f1722 75%)'
                : 'radial-gradient(circle at 50% 30%, #0b1118 0%, #03060a 85%)';
            ctx.clearRect(0, 0, snowCanvas.width, snowCanvas.height);
        }
    }

    btnSeason.addEventListener('click', () => {
        applySeason(!isWinterSeason);
    });

    // =========================================================================
    // Proposal 1: Railway Station Audio Chime (Web Audio API Synthesizer)
    // =========================================================================
    const btnSoundChime = document.getElementById('btnSoundChime');
    let audioCtx = null;

    function playStationChime() {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }

        btnSoundChime.classList.add('active');
        setTimeout(() => btnSoundChime.classList.remove('active'), 1800);

        // Authentic Russian Railways 3-Tone Station Gong (F4 - A4 - C5 triad)
        const notes = [349.23, 440.00, 523.25];
        const times = [0.0, 0.45, 0.90];

        notes.forEach((freq, idx) => {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();

            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime + times[idx]);

            // Subtle harmonic warmth (chime overtone)
            gain.gain.setValueAtTime(0, audioCtx.currentTime + times[idx]);
            gain.gain.linearRampToValueAtTime(0.28, audioCtx.currentTime + times[idx] + 0.04);
            gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + times[idx] + 1.3);

            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.start(audioCtx.currentTime + times[idx]);
            osc.stop(audioCtx.currentTime + times[idx] + 1.35);
        });
    }

    btnSoundChime.addEventListener('click', playStationChime);

    // 4. Day / Night Environment Toggle
    btnToggleTheme.addEventListener('click', () => {
        isDayMode = !isDayMode;
        btnToggleTheme.classList.toggle('active', !isDayMode);
        applySeason(isWinterSeason);
    });

    // 5. Scale Mode (Mockup 1:20 vs Life-size 1:1)
    btnScaleMode.addEventListener('click', () => {
        isScaleMockup = !isScaleMockup;
        if (isScaleMockup) {
            scaleLabel.textContent = 'Макет (Авто)';
            viewer.setAttribute('ar-scale', 'auto');
            if (arScaleText) arScaleText.textContent = 'Макет (Авто)';
        } else {
            scaleLabel.textContent = 'Масштаб 1:1';
            viewer.setAttribute('ar-scale', 'fixed');
            if (arScaleText) arScaleText.textContent = '1:1 (Реальный)';
        }
        btnScaleMode.classList.toggle('active', !isScaleMockup);
    });

    // =========================================================================
    // Feature 1: Guided Tour (Автоматическая кинематографическая экскурсия)
    // =========================================================================
    const btnTour = document.getElementById('btnTour');
    const tourBtnLabel = document.getElementById('tourBtnLabel');
    const tourBanner = document.getElementById('tourBanner');
    const tourStepText = document.getElementById('tourStepText');
    const tourProgressBar = document.getElementById('tourProgressBar');
    const btnStopTour = document.getElementById('btnStopTour');

    const tourNodes = Array.from(hotspots);
    let isTourActive = false;
    let tourIndex = 0;
    let tourTimer = null;
    let tourProgressTimer = null;
    const TOUR_STEP_DURATION = 6500; // 6.5 seconds per node

    function startTour() {
        isTourActive = true;
        tourIndex = 0;
        btnTour.classList.add('active');
        tourBtnLabel.textContent = 'Пауза';
        tourBanner.classList.remove('hidden');
        playStationChime();
        runTourStep();
    }

    function stopTour() {
        isTourActive = false;
        clearTimeout(tourTimer);
        clearInterval(tourProgressTimer);
        btnTour.classList.remove('active');
        tourBtnLabel.textContent = 'Экскурсия';
        tourBanner.classList.add('hidden');
        tourProgressBar.style.width = '0%';
    }

    function runTourStep() {
        if (!isTourActive) return;

        if (tourIndex >= tourNodes.length) {
            tourStepText.textContent = 'Экскурсия завершена! Возврат к общему виду.';
            setTimeout(() => {
                stopTour();
                btnResetCamera.click();
            }, 2500);
            return;
        }

        const node = tourNodes[tourIndex];
        selectHotspot(node);
        tourStepText.textContent = `Узел ${tourIndex + 1} из ${tourNodes.length}: ${node.dataset.title}`;

        const startTime = Date.now();
        clearInterval(tourProgressTimer);
        tourProgressBar.style.width = '0%';

        tourProgressTimer = setInterval(() => {
            const elapsed = Date.now() - startTime;
            const pct = Math.min(100, (elapsed / TOUR_STEP_DURATION) * 100);
            tourProgressBar.style.width = `${pct}%`;
            if (pct >= 100) {
                clearInterval(tourProgressTimer);
            }
        }, 50);

        clearTimeout(tourTimer);
        tourTimer = setTimeout(() => {
            tourIndex++;
            runTourStep();
        }, TOUR_STEP_DURATION);
    }

    btnTour.addEventListener('click', () => {
        if (isTourActive) {
            stopTour();
        } else {
            startTour();
        }
    });

    btnStopTour.addEventListener('click', stopTour);

    // =========================================================================
    // Feature 2: Dimension Lines (Инженерные габариты по ГОСТ 9238)
    // =========================================================================
    const btnDimensions = document.getElementById('btnDimensions');
    const dimHotspots = document.querySelectorAll('.dim-hotspot');
    let dimensionsVisible = false;

    btnDimensions.addEventListener('click', () => {
        dimensionsVisible = !dimensionsVisible;
        btnDimensions.classList.toggle('active', dimensionsVisible);
        viewer.classList.toggle('dimensions-active', dimensionsVisible);
        dimHotspots.forEach(dh => {
            dh.classList.toggle('hidden', !dimensionsVisible);
        });
    });

    // =========================================================================
    // QR Code Modal for Mobile AR launch
    // =========================================================================
    const btnModeWifi = document.getElementById('btnModeWifi');
    const btnModeCustom = document.getElementById('btnModeCustom');
    const customUrlRow = document.getElementById('customUrlRow');
    const targetUrlInput = document.getElementById('targetUrlInput');
    const btnApplyUrl = document.getElementById('btnApplyUrl');
    const activeUrlLabel = document.getElementById('activeUrlLabel');

    // Default WiFi LAN or Hosted URL
    const LOCAL_WIFI_IP = '192.168.100.237';
    const port = window.location.port || '8000';
    const isHosted = window.location.protocol === 'https:' || (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1' && !window.location.hostname.startsWith('192.168.'));
    let currentMobileUrl = isHosted ? window.location.href : `http://${LOCAL_WIFI_IP}:${port}/index.html`;

    if (isHosted && btnModeWifi) {
        btnModeWifi.textContent = 'Текущий сайт (HTTPS)';
    }

    function renderQr(url) {
        currentMobileUrl = url;
        activeUrlLabel.textContent = url;
        qrcodeContainer.innerHTML = '';
        if (typeof QRCode !== 'undefined') {
            new QRCode(qrcodeContainer, {
                text: url,
                width: 180,
                height: 180,
                colorDark: '#0d1117',
                colorLight: '#ffffff',
                correctLevel: QRCode.CorrectLevel.M
            });
        }
    }

    function openQrModal() {
        qrModal.classList.add('active');
        renderQr(currentMobileUrl);
    }

    btnModeWifi.addEventListener('click', () => {
        btnModeWifi.classList.add('active');
        btnModeCustom.classList.remove('active');
        customUrlRow.style.display = 'none';
        renderQr(isHosted ? window.location.href : `http://${LOCAL_WIFI_IP}:${port}/index.html`);
    });

    btnModeCustom.addEventListener('click', () => {
        btnModeCustom.classList.add('active');
        btnModeWifi.classList.remove('active');
        customUrlRow.style.display = 'flex';
        if (targetUrlInput.value.trim()) {
            renderQr(targetUrlInput.value.trim());
        }
    });

    btnApplyUrl.addEventListener('click', () => {
        const val = targetUrlInput.value.trim();
        if (val) {
            renderQr(val);
        }
    });

    btnQr.addEventListener('click', openQrModal);
    closeQrBtn.addEventListener('click', () => qrModal.classList.remove('active'));
    qrModal.addEventListener('click', (e) => {
        if (e.target === qrModal) qrModal.classList.remove('active');
    });

    // Model load notification
    viewer.addEventListener('load', () => {
        console.log('3D Station Pavilion Model loaded successfully in WebXR viewport.');
    });

    // WebXR / AR status listeners
    viewer.addEventListener('ar-status', (event) => {
        console.log('WebXR AR Status changed:', event.detail.status);
    });
});
