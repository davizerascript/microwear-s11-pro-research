import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.InstructionIterator;

public class AnalysisSummary extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("program=" + currentProgram.getName());
        println("language=" + currentProgram.getLanguage().getLanguageID());
        println("imageBase=" + currentProgram.getImageBase());
        long functionCount = currentProgram.getFunctionManager().getFunctionCount();
        println("functionCount=" + functionCount);
        long instructionCount = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext()) {
            instructions.next();
            instructionCount++;
        }
        println("instructionCount=" + instructionCount);
        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        int shown = 0;
        while (functions.hasNext() && shown < 100) {
            Function f = functions.next();
            println("function " + f.getEntryPoint() + " " + f.getName() + " body_bytes=" + f.getBody().getNumAddresses());
            shown++;
        }
        println("functionSampleCount=" + shown);
    }
}
