<template>
    <div v-if="!isQuizPage" id="footer">
        <div class="footer-content">
            <div class="about-section">
                <p>
                    Play'n'trade est une plateforme pour les passionnées de jeux de société. Grace à son marketplace et son système d'échange, il permet de faire avancer la communauté des joueurs de jeux de société..
                </p>
                <a href="/about" class="about-link">A propos de Play'n'trade</a>
            </div>
        </div>
        <div class="watermark">
            © 2025 Play'n'trade. Tous droits réversés.
        </div>
    </div>
</template>

<script>
export default {
    name: 'FooterView',
    computed: {
    },
};
</script>

<style scoped>
#footer {
    background-color: var(--pnt-black);
    color: white;
    padding: 20px 10px;
    text-align: center;
    position: relative;
    margin-top: 50px;
    user-select: none;
}

.footer-content {
    max-width: 1200px;
    margin: 0 auto;
}

.about-section {
    margin-bottom: 15px;
}

.about-section p {
    font-size: 14px;
    margin-bottom: 10px;
}

.about-link {
    color: var(--pnt-primary);
    text-decoration: none;
    font-weight: bold;
}

.about-link:hover {
    text-decoration: underline;
}

.watermark {
    margin-top: 20px;
    font-size: 12px;
    opacity: 0.6;
}
</style>
