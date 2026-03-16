import {Prism as SyntaxHighlighter} from "react-syntax-highlighter"
import {oneDark} from "react-syntax-highlighter/dist/cjs/styles/prism"

export default function CodeBlock({language, value}: { language: string, value: string }) {

    return (

        <SyntaxHighlighter
            language={language}
            style={oneDark}
        >

            {value}

        </SyntaxHighlighter>

    )

}