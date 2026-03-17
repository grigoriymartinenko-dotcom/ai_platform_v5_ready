import ChatInterface from "../components/ChatInterface";

export default function ChatPage() {

    return (

        <div style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "100vh",
            background: "#f5f5f5"
        }}>

            <div style={{width: "800px"}}>

                <h1 style={{
                    textAlign: "center",
                    marginBottom: "20px"
                }}>
                    AI Platform v5
                </h1>

                <ChatInterface/>

            </div>

        </div>

    );

}