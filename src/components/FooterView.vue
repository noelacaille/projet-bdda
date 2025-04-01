<template>
    <div v-if="!isQuizPage" id="footer">
        <div class="footer-content">
            <div class="about-section">
                <p>
                    CineQuizz is a cinema quiz platform where movie enthusiasts can test their knowledge and learn more
                    about their favorite films.
                </p>
                <a href="/about" class="about-link">Learn More</a>
            </div>
        </div>
        <div class="watermark">
            © 2024 CineQuizz. All rights reserved.
        </div>
    </div>
</template>

<script>
export default {
    name: 'FooterView',
    computed: {
        isQuizPage() {
            return this.$route.path === '/quiz';
        },
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
