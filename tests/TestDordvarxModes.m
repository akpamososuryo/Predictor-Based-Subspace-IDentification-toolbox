classdef TestDordvarxModes < matlab.unittest.TestCase
    properties
        RepoRoot
    end

    methods (TestMethodSetup)
        function addToolboxToPath(testCase)
            testCase.RepoRoot = fileparts(fileparts(mfilename('fullpath')));
            addpath(testCase.RepoRoot);
        end
    end

    methods (TestMethodTeardown)
        function removeToolboxFromPath(testCase)
            rmpath(testCase.RepoRoot);
        end
    end

    methods (Test)
        function baselineWeightAndNoDRun(testCase)
            d = testutils.makeDordvarxData('seed', 73);

            [S0, X0, V0, U0, Z0] = dordvarx(d.u, d.y, d.f, d.p, 'none', 'gcv', 0, 0);
            testCase.verifyTrue(isvector(S0));
            testCase.verifyTrue(ismatrix(X0));
            testCase.verifyTrue(ismatrix(V0));
            testCase.verifyTrue(ismatrix(U0));
            testCase.verifyTrue(ismatrix(Z0));
            testCase.verifyTrue(all(isfinite(S0(:))));

            [S1, X1, V1] = dordvarx(d.u, d.y, d.f, d.p, 'none', 'gcv', 1, 0);
            testCase.verifyTrue(isvector(S1));
            testCase.verifyTrue(ismatrix(X1));
            testCase.verifyTrue(ismatrix(V1));

            [S2, X2, V2] = dordvarx(d.u, d.y, d.f, d.p, 'none', 'gcv', 0, 1);
            testCase.verifyTrue(isvector(S2));
            testCase.verifyTrue(ismatrix(X2));
            testCase.verifyTrue(ismatrix(V2));
        end
    end
end
