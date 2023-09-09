import { Inter } from "@next/font/google";

const inter = Inter({ subsets: ["latin"] });

export default function MyApp({ Component, pageProps }) {
    return (
        <main>
            <Component {...pageProps} />
        </main>
    );
}