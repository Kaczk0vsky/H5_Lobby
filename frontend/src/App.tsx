// import ListGroup from "./components/ListGroup";
import Alert from "./components/Alert";
import Button from "./components/Button";
import { useState } from "react";

function App() {
  // let items = [
  //   "Dragon Claw",
  //   "Ring of the broken will",
  //   "Dwarfen schield",
  //   "Necromancy necklecke",
  // ];
  const[alertVisible, setAlertVisibility] = useState(false)
  // const handleSelectItem = (item: string) => {
  //   console.log(item);
  // };

  return (
    <div>
      {/* <ListGroup
        items={items}
        heading="Artifacts"
        onSelectItem={handleSelectItem}
      /> */}
      {alertVisible && <Alert onClose={() => setAlertVisibility(false)}><span>Work in progress... Come back later!</span></Alert>}
      <Button color="warning" onClick={() => setAlertVisibility(true)}>Click Me!</Button>
    </div>
  );
}

export default App;
