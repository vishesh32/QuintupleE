interface Variables {
    name: string,
    value: string
}

const AllVars : Variables[] = [
    {
        name: "Buy Price (Cents)",
        value: "buy_price",
    },
    {
        name: "Sell Price (Cents)",
        value: "sell_price",
    },
    {
        name: "Demand (Watts)",
        value: "demand",
    },
    {
        name: "Irradiance (%)",
        value: "sun",
    }
];

export { AllVars }